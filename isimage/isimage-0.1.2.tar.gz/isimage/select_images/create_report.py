import os
import markup

def relpath_same_drive(p1, p2):
    """ 
        Convert p1 into path relative to p2 if both on the same drive.
    """

    dr = os.path.splitdrive(p1)[0]
    if len(dr) == 0 or dr == os.path.splitdrive(p2)[0]:
        return os.path.relpath(p1, p2)
    return p1    

def create_report(path, gs):
    """ Creates html report from the list of GeneStage objects """
    folder = os.path.split(path)[0]
    html_folder = os.path.join(folder, 'html')
    if not os.path.exists(html_folder):
        os.makedirs(html_folder)

    result_page = markup.page()
    result_page.init()
    
    genes = {}
    for g in gs:
        if g.gene not in genes:
            genes[g.gene] = []
            
        genes[g.gene] += [g]

    for gene, gl in sorted(genes.items(), key=lambda x: x[0]):
        for g in sorted(gl, key = lambda x: x.stage):
            stage_path = os.path.join(html_folder, gene + '_' + str(g.stage) + '.html')

            stage_page = markup.page()
            stage_page.init()
            for name in g.names:
                img = g.find_images(name)
                stage_page.a(markup.oneliner.img(src=relpath_same_drive(name, html_folder), height=100), href=relpath_same_drive(name, html_folder))
                if len(img) > 0 and hasattr(img[0], "saved_name"):
                    stage_page.a(markup.oneliner.img(src=relpath_same_drive(img[0].saved_name, html_folder), height=100), href=relpath_same_drive(img[0].saved_name, html_folder))
                stage_page.hr()            
            print >>open(stage_path, 'w'), stage_page                

            result_page.h4(gene)
            result_page.br()
            result_page.a('Stage ' + str(g.stage), href=os.path.relpath(stage_path, folder))
            result_page.br()
            for i, cls in enumerate(g.cleared):
                if len(cls) > 0:
                    cluster_path = stage_path[:-4] + '_c' + str(i) + '.html'

                    cluster_page = markup.page()
                    cluster_page.init()

                    cluster_page.a(markup.oneliner.img(src=relpath_same_drive(cls.best().saved_name, html_folder), height=200, alt='No good'), href=relpath_same_drive(cls.best().saved_name, html_folder))
                    
                    cluster_page.hr()            
                    for img in cls:
                        cluster_page.a(markup.oneliner.img(src=relpath_same_drive(img.saved_name, html_folder), height=75, alt='No good'), href=relpath_same_drive(img.saved_name, html_folder))
                    print >>open(cluster_path, 'w'), cluster_page                
                    
                    result_page.a(markup.oneliner.img(src=relpath_same_drive(cls.best().saved_name, folder), height=75, alt='No good'), href=os.path.relpath(cluster_path, folder))

            for i, cls in enumerate(g.uncleared):
                if len(cls) > 0:
                    cluster_path = stage_path[:-4] + '_u' + str(i) + '.html'

                    cluster_page = markup.page()
                    cluster_page.init()

                    cluster_page.a(markup.oneliner.img(src=relpath_same_drive(cls.best().saved_name, html_folder), height=200, alt='No good'), href=relpath_same_drive(cls.best().saved_name, html_folder))
                    cluster_page.hr()            
                    for img in cls:
                        cluster_page.a(markup.oneliner.img(src=relpath_same_drive(img.saved_name, html_folder), height=75, alt='No good'), href=relpath_same_drive(img.saved_name, html_folder))
                    print >>open(cluster_path, 'w'), cluster_page                
                        
                    result_page.a(markup.oneliner.img(src=relpath_same_drive(cls.best().saved_name, folder), height=75, alt='No good'), href=os.path.relpath(cluster_path, folder))
                
            result_page.hr()
                
    print >>open(path, 'w'), result_page
