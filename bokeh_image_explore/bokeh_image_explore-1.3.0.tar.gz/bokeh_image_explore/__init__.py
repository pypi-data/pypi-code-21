from bokeh.plotting import output_notebook, figure, show
from bokeh.models import ColumnDataSource, CustomJS, Rect, ImageURL

def explore_embedding(X, urls, title='Embedding', size=2, plot_width=800, qsize=10, plot_height=None, colors=None):
    source_all_imgs = ColumnDataSource({"img_urls": urls})
    source_only_these_imgs = ColumnDataSource({"img_urls": [], "x": [], "y": [], "w" : [], "h": []})
    if colors:
        source = ColumnDataSource({"x": X[:,0], "y": X[:,1], "color": colors})
    else:
        source = ColumnDataSource({"x": X[:,0], "y": X[:,1]})

    p1 = figure(title = title,
                # tools = 'box_zoom,wheel_zoom,pan,reset',
                plot_width = plot_width,
                plot_height = plot_height or int(plot_width*3.0/4.0),
    )
    imgs = ImageURL(url = "img_urls",
                    x = "x", y = "y",
                    w = "w", h = "h",
                    anchor = "bottom_left",
                    global_alpha = 1.0
    )
    p1.add_glyph(source_only_these_imgs, imgs)
    kwargs = dict(fill_color="color") if colors else dict()
    p1.scatter(x = "x",
               y = "y",
               source = source,
               size = size,
               fill_alpha = 1.0,
               line_color = None,
               **kwargs
    )
    js_cb = CustomJS(args=dict(source=source_only_these_imgs,
                               source_all_imgs=source_all_imgs,
                               source_locs=source,
                               xrange = p1.x_range,
                               yrange = p1.y_range,
                               imgs = imgs,
                               ),
                     code="""

                function update(){
                    // Quantize all the images in 'source_all_imgs'.
                    var xs = source_locs.get('data')['x'],
                        ys = source_locs.get('data')['y'],
                        urls = source_all_imgs.get('data')['img_urls'],
                        xmin = xrange.get('start'),
                        xmax = xrange.get('end'),
                        ymin = yrange.get('start'),
                        ymax = yrange.get('end'),
                        QSIZE = (xmax - xmin) / %d;
                    var quantized_helper = {},
                        result_urls = [], result_x = [], result_y = [],
                        result_w = [], result_h = [];

                    for (var i=0; i<xs.length; i++) {
                        if (result_urls.length > 1000) break;
                        var x = xs[i], y = ys[i];
                        if (x > xmin && x < xmax && y > ymin && y < ymax) {
                            // Quantize this
                            var qx = Math.floor((x - xmin) / QSIZE),
                                qy = Math.floor((y - ymin) / QSIZE),
                                qkey = qx+"--"+qy;
                           if (!(qkey in quantized_helper) && urls[i]) {
                               quantized_helper[qkey] = true;
                               x = (qx * QSIZE) + xmin;
                               y = (qy * QSIZE) + ymin;
                               result_x.push(x);
                               result_y.push(y);
                               result_w.push(QSIZE);
                               result_h.push(QSIZE);
                               result_urls.push(urls[i]);
                           }
                        }
                    }
                    data = source.get('data');
                    data['x'] = result_x;
                    data['y'] = result_y;
                    data['w'] = result_w;
                    data['h'] = result_h;
                    data['img_urls'] = result_urls;
                    //console.log(data);
                    //console.log("QSIZE is", QSIZE);
                    imgs.attributes.global_alpha = 1.0;
                    source.trigger('change');
                }
                // Trigger change... but ONLY once!
                if (window.timer) {clearTimeout(window.timer);}
                window.timer = setTimeout(update, 1000);

                // Instantly clear while zooming.
                //data = source.get('data');
                //data['img_urls'] = data['x'] = data['y'] = data['w'] = data['h'] = [];
                imgs.attributes.global_alpha = 0.2;
                //source.trigger('change');
                     """%qsize)

    p1.x_range.callback = js_cb
    p1.y_range.callback = js_cb

    return p1
