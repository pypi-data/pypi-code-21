# -*- coding:utf-8 -*-
from selenium.webdriver.common.proxy import *
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotVisibleException, WebDriverException
from selenium.webdriver import  ActionChains

from qlib.log import show
from bs4 import BeautifulSoup as BS
from bs4.element import NavigableString, Tag
from hashlib import md5
import os, socket, time
import logging , re
import configparser

logging.basicConfig(level=logging.INFO)


phantomjs_path = os.popen("which phantomjs").read().strip()
chrome_path  = os.popen("which chromedriver").read().strip()
firefox_path  = os.popen("which chromedriver").read().strip()
if not phantomjs_path:
    show("install phantomjs first!!")
    sys.exit(1)


SocialKit_cache_max_size = '1000468'
storage_path = '/tmp/'
cookies_path = '/tmp/cookie.txt'

class ProxyNotConnectError(Exception):
    pass


def test_proxy(proxy):
    t,s,p = proxy.split(":")
    s = s[2:]
    p = int(p)
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((s,p))
    except Exception as e:
        show(e)
        return False
    return True



class FLowNet:
    keys = Keys
    def __init__(self, url=None, proxy=False, load_img=False, driver=None, random_agent=False, agent=None,**options):
        
        if proxy:
            if not test_proxy(proxy):
                raise ProxyNotConnectError(proxy + " not connected")

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        if agent:
            dcap["phantomjs.page.settings.userAgent"] = agent

        # dcap['phantomjs.page.settings.resourceTimeout'] = '5000'
        load_image = 'true' if load_img else 'false' 
        timeout = options.get('timeout')

        web_service_args = [
            '--load-images=' + load_image,
        ]

        if proxy:
            proxy_t, proxy_c = proxy.split("//")
            proxy_t = proxy_t[:-1]
            show(proxy_c, proxy_t)
            web_service_args += [
                '--proxy=' + proxy_c,
                '--proxy-type=' + proxy_t,
                '--local-storage-path=' + storage_path,
                '--cookies-file=' + cookies_path,
                '--local-storage-quota=' + str(SocialKit_cache_max_size),
            ]
        if driver:

            if 'chrome' in driver:
                chrome_options = webdriver.ChromeOptions()
                if proxy:
                    chrome_options.add_argument('--proxy-server=%s' % proxy)
                
                if os.path.exists(driver):
                    self.phantom = webdriver.Chrome(driver, chrome_options=chrome_options, service_args=web_service_args, desired_capabilities=dcap)
                else:
                    self.phantom = webdriver.Chrome(chrome_path, chrome_options=chrome_options, service_args=web_service_args, desired_capabilities=dcap)

            elif 'fir' in driver:
                if os.path.exists(driver):
                    self.phantom = webdriver.Firefox(driver, service_args=web_service_args, desired_capabilities=dcap)
        else:
            self.phantom = webdriver.PhantomJS(phantomjs_path,service_args=web_service_args, desired_capabilities=dcap)


        if 'width' in options:
            self.phantom.set_window_size(options.get('width', 1024), options.get('height', 768))
        if timeout:
            self.phantom.set_page_load_timeout(int(timeout))
        self.dcap = dcap
        self.datas = []
        self.render_text = {}
        self.count_for_time = 0
        self.count_type = 'int'
        if url:
            self.go(url)

        self.current_page_point = self.current_point
        self.current_point_y = self.current_page_point[1]
        self.current_point_x = self.current_page_point[0]
        self.read_flags_count = {}

    @property
    def current_point(self):
        xy = self.phantom.get_window_position()
        return xy['x'], xy['y']

    @property
    def height(self):
        return self.phantom.get_window_size()['height']

    @property
    def width(self):
        return self.phantom.get_window_size()['width']


    def scroll_down_next_page(self):
        
        self.current_point_y += self.height
        self.scroll(self.current_point_y)

    def scroll_up_before_page(self):
        self.current_point_y -= self.height
        if self.current_point_y <= 0:
            self.current_point_y = 1
        self.scroll(self.current_point_y)


    def extract_S(self, loc):
        id_i = loc.find("#")
        class_i = loc.find(".")

        if id_i < class_i:
            tag = loc[:id_i].lower()
            id_s = loc[id_i:class_i]
            class_s = loc[class_i:]

        else:
            tag = loc[:class_i].lower()
            class_s = loc[class_i:id_i]
            id_s = loc[id_i:]

        return tag, class_s, id_s

    def scroll(self, y):
        # last_height = driver.execute_script("return document.body.scrollHeight")
        self.phantom.execute_script("window.scrollTo(1, %d);" % y)


    def flow(self,loc, ac, cursor, screenshot=True, submit=False, **kargs):
        """
        exm:
            #main/C
            .in/I'hello,work\n',.in-2/I'if no .in this will be flow'->[cond2]
            .over/C
            [cond2]#rechck/I'hello,work'



            action : I = input / C = click / D = clear / M = move scroll
        """
        if_screenshot = screenshot
        text = None
        show("--- ", cursor, " ---",color='green')
        if '->' in ac:
            ac, cursor =  ac.split("->")
        else:
            cursor += 1

        if '{' in ac and '}' in ac:
            show("render:", ac)
            key = re.findall(r'\{(.+?)\}', ac)[0]
            if key in self.render_text:
                ac = ac.format(**{key: self.render_text[key]})
            else:
                show("no found key:", key , " in render", color='red', log=True, k='error')

        if '[' in loc and ']' in loc:
            text = re.findall(r'\[(.+?)\]', loc)[0]
            loc = re.sub(r'\[(.+?)\]', '', loc)
            show('find text:',text)

        elif loc.startswith("-"):
            real_point = loc[1:]
            if len(real_point) >= 1:
                
                if real_point[0] in '0123456789':
                    real_point_y = int(real_point.strip())
                    self.scroll(real_point_y)
                elif real_point[0] == '>':
                    self.scroll_down_next_page()
                elif real_point[0] == '<':
                    self.scroll_up_before_page()
                



        # show(cursor, loc, ac)
        if ac[0] == 'C':
            show('click:', loc, text)
            option = False
            if '[' in ac and ']' in ac:
                
                option = re.findall(r'\[([\w\W]+)\]', ac)[0]
                show("option:", option, color='red')
            self.do(loc, text=text, option=option, **kargs)
            
        elif ac[0] == 'I':
            msg = re.findall(r'\'([\w\W]+)\'', ac)
            show('type:', msg, 'in',loc, text)
            self.do(loc, msg,text=text, **kargs)

            if ac.endswith("R"):
                self.do(loc, '\n',text=text, **kargs)
            # self.do(loc, text=text, **kargs)
        elif ac[0] == 'D':
            show('clear:', loc, text)
            self.do(loc, clear=True,text=text, **kargs)
        elif ac[0] == 'M':
            pass
        elif ac[0] == 'S':
            if '[' in ac:
                msg = re.findall(r'\'([\w\W]+)\'', ac)[0]
                show("screenshot as : ", msg)
                self.screenshot(msg)
                return cursor


        if if_screenshot:
            show("screen:", cursor)
            self.screenshot(str(cursor))

        return cursor

        
    def parse_render_text(self, f):
        with open(f) as fp:
            for l in fp:
                k,v = l.split(":", maxsplit=1)
                self.render_text[k] = v

    def check(self, condition):
        if not hasattr(self,  "flag_for_condition"):

            self.flag_for_condition = condition
            if isinstance(condition, int):
                self.count_type = 'int'
                self.count_for_time = 0
        else:
            if self.count_type == 'int':
                self.count_for_time += 1

        if self.count_for_time >= int(condition): return True

        if self.flag_for_condition == 'IndexOver':return True
        
        return False


    def read_lines(self, fp, **kargs):
        """
        read all commands and render text in command if command exists '{sss}'
        """
        fps = {}
        for k in kargs:
            fps[k] = [i.strip() for i in open(kargs[k]).readlines() if os.path.exists(kargs[k])]

        for n,i in enumerate(fp.readlines()):

            flow = i.strip()
            if "{" in flow and '}' in flow:
                keys = dict.fromkeys(re.findall(r'{(\w+?)}', flow), None)
                for k in keys:
                    if k not in self.read_flags_count:
                        self.read_flags_count[k] = 0
                    else:
                        self.read_flags_count[k] += 1
                    keys[k] = fps[k][self.read_flags_count]
                flow = flow.format(**keys)
                yield flow



    def flow_doc(self, f, render_text=None, test=False, timeout=7, **kargs):
        """
        exm:
            #main/C
            .in/I'hello,work\n',.in-2/I'if no .in this will be flow'->[cond2]
            .over/C
            [cond2]#rechck/I'hello,work'
        """
        if render_text:
            self.parse_render_text(render_text)

        self.render_text.update(kargs)

        if os.path.exists(f):
            flows = self.read_lines(open(f), **kargs)
            
        elif isinstance(f, list):
            flows = f
        else:
            flows = f.split('\n')
        
        cursor = 0
        wait = 0
        for_end = False
        for_start = False
        if_start = False
        if_end = False
        mul_start_ele = []
        for_time = None
        if_pass = False
        for_point = None
        for_cursor = -1
        while 1:

            if_submit = False
            if cursor >= len(flows):
                show("cursor break", cursor)
                break
            pre_order = flows[cursor]
            show("==", cursor,pre_order, for_time, color='green')

            if pre_order.startswith("+") and for_start:
                plus_num = int(pre_order[1:])
                for_time += plus_num
                show("for time jump to :", for_time)
                cursor += 1
                pre_order = flows[cursor]

            if pre_order.startswith("endif"):
                cursor += 1
                if if_start:
                    if_start = False
                    if_end = False
                    if_pass = False
                continue
            elif if_pass:
                cursor += 1
                continue

            if pre_order.startswith('for') and for_start != True:
                for_start = True
                for_time = 0
                _, condition, pre_order = pre_order.split("::")
                show("for mode", "start")
                mul_start_ele = list(self.finds(pre_order.split("/")[0]))
                for_point = cursor


            elif pre_order.startswith('for') and for_start:
                _, condition, pre_order = pre_order.split("::")
                for_time += 1
                
                
            if pre_order.startswith("if"):
                show("--- ","if mode"," ---", color='green')
                _, pre_order = pre_order.split("::")
                www = self.find(pre_order)
                if www and www.is_displayed():
                    cursor += 1
                    if_start = True
                else:
                    if_start = True
                    if_pass = True
                    cursor += 1
                continue

            

                
            if pre_order.startswith("endfor"):
                for_cursor = cursor+1
                if test:
                    pass
                else:
                    if self.check(condition):
                        show("for end")
                        for_end = True
                        pass

                if for_time:
                    if for_time >= len(mul_start_ele):
                        show("for end list")
                        for_end = True
                # else:
                    # cursor+=1
                    # continue
                
                if for_end:
                    for_time = None
                    for_cursor = -1
                    for_start = False
                    for_end = False

                    # jump out from for
                    cursor += 1
                else:
                    # for_time += 1

                    cursor = for_point
                show("jump to ", cursor)
                continue


            # 结束标志
            if pre_order == '[over]':
                show("over")
                break

            #  submit flag
            if "I'" in pre_order:
                if cursor + 1 < len(flows):
                    if "I'" in flows[cursor+1]:
                        if_submit = False
                    else:
                        if_submit = True


            # [正则匹配标志] 为最短路径选取
            if '[' in pre_order:
                wait = timeout

            # 强置等待时间
            if pre_order[0] in '0123456789' and pre_order[-1] in '0123456789':
                show("wait :", pre_order)
                self._wait(int(pre_order))
                cursor += 1
                continue

            if pre_order.startswith("http"):
                show("--> ", pre_order)
                if test:
                    show(pre_order, color='yellow')
                else:
                    self.go(pre_order) 
                cursor += 1
                continue
            show(cursor, pre_order)



            if ',' in pre_order:
                conditions = pre_order.split(",")
                for i in conditions:
                    loc, ac =  i.split("/")
                    loc = loc.strip()
                    ac = ac.strip()
                    if test:
                        show(loc, ac, cursor, wait, if_submit, color='yellow')
                        cursor +=1
                    else:
                        cursor =  self.flow(loc, ac, cursor, wait=wait, submit=if_submit, for_time=for_time, **kargs)
            
            # scroll mode
            elif pre_order.startswith('-'):
                point, ac =  pre_order.split("/")
                cursor  = self.flow(point, ac, cursor, wait=wait, submit=if_submit, for_time=for_time, **kargs)

            # normal css select mode
            else:
                loc, ac =  pre_order.split("/")
                loc = loc.strip()
                ac = ac.strip()
                if test:
                    show(loc, ac, cursor, wait, if_submit, color='yellow')
                    cursor +=1
                else:
                    cursor =  self.flow(loc, ac, cursor,wait=wait, submit=if_submit, for_time=for_time,**kargs)

        # clear read_flag_count
        self.read_flags_count = {}


    def go(self, url):
        self.phantom.get(url)
        self.soup = BS(self.phantom.page_source, 'lxml')

    def _wait(self, selector, timeout=7):
        if isinstance(selector, int):
            time.sleep(selector)
        return None

        if '[' in selector:
            selector = selector[:selector.find('[')]
        try:
            if '.' in selector:
                wait = WebDriverWait(self.phantom,timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME,selector[1:])))
            elif '#' in selector:
                wait = WebDriverWait(self.phantom,timeout).until(
                    EC.presence_of_element_located((By.ID,selector[1:])))
            else:
                wait = WebDriverWait(self.phantom,timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME,selector)))
        except Exception as e:
            self.screenshot('debug')
            raise e

    def save_tmp(self, key=None):
        if self.phantom.current_url in self.datas:
            self.datas[self.phantom.current_url].append(self.phantom.page_source)
        else:
            self.datas[self.phantom.current_url] = [self.phantom.page_source]

    def screenshot(self, *names):
        if len(names) > 0:
            self.phantom.get_screenshot_as_file('/tmp/' + names[0]+".png")
        else:
            self.phantom.get_screenshot_as_file('/tmp/one.png')

    def do(self, selectID, *args, text=None,save_screen=True,save_data=False, wait=None, clear=False, callback=None, for_time=None,**kargs):
        """
        css select mode :
            div .
        """
        # before_hash = md5(self.phantom.page_source.encode("utf8")).hexdigest()
        if save_screen:
            self.screenshot()
        selectID = selectID.strip()
        if '>' in selectID:
            self._wait(selectID.split(">")[-1])
        else:
            self._wait(selectID)
        res = None



        if text:
            if for_time and isinstance(for_time, int):
                try:
                    targets = list(self.back_recur_finds(selectID, text))
                    while 1:
                        target = targets[for_time]
                        if target.is_displayed():
                            break
                        for_time += 1

                except IndexError:
                    show("index over: ", for_time)
                    self.flag_for_condition = 'IndexOver'
                    return self
            else: 
                target = self.back_recur_find(selectID, text)
            if not target:
                self._wait(1)
                for i in range(5):
                    show("try ", i,"time...")
                    if save_screen:
                        self.screenshot()
                    self._wait(wait)
                    target = self.back_recur_find(selectID, text)
                    if target:
                        break

            if not target:
                raise NoSuchElementException()

        else:
            target = self.find(selectID)

        if not target:
            show("Not found :", selectID, color='yellow', log=True, k='warn')
            return self

        if clear:
            show("clear :",selectID, log=True, k='debug')
            target.clear()

        #####
        # actions area
        self.old_data = self.phantom.page_source

        if len(args) == 1:
            try:
                ac = ActionChains(self.phantom)
                ac.move_to_element(target).click().send_keys(args[0]).perform()
            except WebDriverException as e:
                show("input not work,may be no element focus,try action-chains mode ...", color='yellow')
                show(selectID, *args, **kargs)
                ac = ActionChains(self.phantom)
                # if 'cannot focus element' in e.msg:
                ac.move_to_element(target).click().send_keys(args[0]).perform()


        elif len(args) == 0:
            ac = ActionChains(self.phantom)
            ac.move_to_element(target).perform()
            if target.tag_name == 'a' and 'javascript' not in target.get_attribute("href"):
                show("directly go -> ",target.get_attribute("href"))
                self.go(target.get_attribute("href"))

            else:
                show("click: ",target.get_attribute("href"))
                try:
                    ac = ActionChains(self.phantom)
                    ac.move_to_element(target).click(target).perform()
                except ElementNotVisibleException:
                    show("normal mode not work , button not visible, try action-chains mode ...", color='yellow')
                    ac = ActionChains(self.phantom)
                    ac.move_to_element(target).click().perform()
                except WebDriverException as we:
                    ccc = 0
                    while 1:
                        # if "Other element would receive the clic" in we.msg:
                        try:
                            show("[2] normal mode not work , button not visible, try action-chains mode ...", color='yellow')
                            ac = ActionChains(self.phantom)
                            ac.move_to_element(target).click().perform()
                        except WebDriverException as we:
                            if "is not clickable at point" in we.msg:
                                ccc += 1
                                if ccc > 4:
                                    raise we
                                continue
                        # else:
                            # raise we
                        break

        else:
            raise Exception("no such operator!!")


        #####    
        # actions after area

        # check if click action is work 
        if len(args) == 0 and kargs.get("option", False) == "check":
            show("<check>", color='red')
            if not self._check_if_clicked():
                pre_nodes_time = 0
            else:
                pre_nodes_time = 2

            while pre_nodes_time < 2:
                show("[",pre_nodes_time,"]","upper node: ", target.tag_name, color='blue')
                if not self._check_if_clicked():
                    show('click not work , try javascript mode...')
                    self.phantom.execute_script("arguments[0].click();", target)
                    if self._check_if_clicked():
                        show("javascript mode work", color='green')
                    else:
                        show('click not work , try javascript mode...[2]')
                        time.sleep(1)
                        self.phantom.execute_script("arguments[0].click();", target)
                        if self._check_if_clicked():
                            show("javascript mode work", color='green')

                if not self._check_if_clicked():
                    target = target.find_element_by_xpath("..")
                    try:
                        target.click()
                    except ElementNotVisibleException:
                        show("normal mode not work , button not visible, try action-chains mode ...", color='yellow')
                        ac = ActionChains(self.phantom)
                        ac.move_to_element(target).click().perform()
                    except WebDriverException as ex:
                        show(ex)
                        pass

                pre_nodes_time += 1

        if wait:
            if isinstance(wait, str):
                self._wait(wait)
            elif isinstance(wait, int):
                time.sleep(wait)
            else:
                show("unknow wait type: (only: int, str)", color='red')

        if callback:
            callback(self.phantom.page_source)

        if save_data:
            if isinstance(save_data, bool):
                self.save_tmp()
            elif isinstance(save_data, str):
                # a fliter ...
                pass
        if save_screen:
            self.screenshot()

        return self

    def _get_absolute_path(self, ele):
        f = ele.name
        if 'id' in ele.attrs:
            f += '#'+ele.attrs['id']
        elif 'class' in ele.attrs:
            f += '#'+ ele.attrs['class']

        while 1:
            if ele.parent.name in  ('body', 'html'):
                break
            ele = ele.parent

            tmp = ele.name
            if 'id' in ele.attrs:
                tmp += '#' + ele.attrs['id']
            elif 'class' in ele.attrs:
                tmp += '#' + ele.attrs['class'][0]
            f = tmp + ">" + f

        return f


    def search(self, css_select, key_text, parser='lxml'):
        b = BS(self.html(), 'lxml')
        for module in b.find_all(text=re.compile(key_text)):
            path = self._get_absolute_path(module.parent)
            if css_select in path:
                return path

    def back_tree(self, t, key, coefficient=0):
        
        if t.find(text=re.compile('(' + key + ')')):
            return t,coefficient
        else:
            coefficient += 1
            if t.parent:
                return self.back_tree(t.parent, key, coefficient)
            else:
                return None, 9999

    def back_include(self, t, css):
        idv = ''
        clv = ''
        old_c = css

        if '.' in css:
            clv = re.findall(r'(\.[\w\-]+)', css)[0][1:]
            css = re.sub(r'(\.[\w\-]+)','', css)
        if '#' in css:
            idv = re.findall(r'(\#[\w\-]+)', css)[0][1:]
            css = re.sub(r'(\#[\w\-]+)','', css)

        if '>' in css:
            css = css.split(">")[-1].lower()

        # show('css:',css,'class:',clv, 'id:',idv)
        r = t.find(css, class_=clv, id=idv)
        if r:
            
            return r
        else:
            if t.parent:
                return self.back_include(t.parent, old_c)
            else:
                show("top", color='red')
                return None

    def extract_css_select(self,css):
        ccl = ''
        idd = ''

        mo = css
        if '.' in mo:
            ccl = re.findall(r'(\.[\w\-]+)', mo)[0]
            mo = re.sub(r'(\.[\w\-]+)','', mo)

        if '#' in mo:
            idd = re.findall(r'(\#[\w\-]+)', mo)[0]
            mo = re.sub(r'(\#[\w\-]+)','', mo)

        if '>' in mo:
            mo = ' > '.join(mo.split('>')).lower()
            last = mo.split(">")[-1].strip()
        else:
            last = mo.strip()

        return mo, ccl, idd,  last

    def back_recur_finds(self, css, key):
        targets = self.phantom.find_elements_by_css_selector(css)
        self.soup = BS(self.phantom.page_source, 'lxml')
        search_ele = ''
        if '|' in key:
            search_ele, key = key.split("|")

        if len(targets) > 1:
            
            mo,mc,mi,_ = self.extract_css_select(css)
            eles = self.soup.select(mo + mc + mi)
            
            try:
                if search_ele:
                    search_ele, cls, ids, last = self.extract_css_select(search_ele)
                    show('select:', search_ele, "class:",cls, "id:",ids, key)
                    for e in self.soup(last, class_=cls[1:], id=ids[1:], text=re.compile(key)):
                        may_e = self.back_include(e.parent, css)
                        if not may_e:
                            return None

                        for i, p in enumerate(eles):
                            if p == may_e:
                                try:
                                    yield targets[i]
                                except IndexError:
                                    continue

                            
                    
                else:
                    for e in self.soup(text=re.compile(key)):
                        may_e = self.back_include(e.parent, css)
                        if not may_e:
                            return None

                        for i, p in enumerate(eles):
                            if p == may_e:
                                try:
                                    yield targets[i]
                                except IndexError:
                                    continue

            except IndexError:
                pass
            
            


    def back_recur_find(self, css, key):
        targets = self.phantom.find_elements_by_css_selector(css)
        self.soup = BS(self.phantom.page_source, 'lxml')
        search_ele = ''
        if '|' in key:
            search_ele, key = key.split("|")

        if len(targets) > 1:
            
            mo,mc,mi,_ = self.extract_css_select(css)
            eles = self.soup.select(mo + mc + mi)
            
            try:
                if search_ele:
                    search_ele, cls, ids, last = self.extract_css_select(search_ele)
                    show('select:', search_ele, "class:",cls, "id:",ids, key)
                    e = self.soup(last, class_=cls[1:], id=ids[1:], text=re.compile(key))[0]
                    
                else:
                    e = self.soup(text=re.compile(key))[0]

            except IndexError:
                return None
            
            may_e = self.back_include(e.parent, css)

            if not may_e:
                return None

            for i, p in enumerate(eles):
                if p == may_e:
                    try:
                        show("got:",i)
                        return targets[i]
                    except IndexError:
# this is condition when some element loaded but other is loading. this may cause 
# 'targets' is not same as 'eles'
                        return None
        else:
            try:
                return targets[0]
            except IndexError:
                return None



    def related_find(self, css_selector, key=''):
        targets = self.phantom.find_elements_by_css_selector(css_selector)
        self.soup = BS(self.phantom.page_source, 'lxml')
        if len(targets) > 1:
            eles = self.soup(css_selector)
            ele,max_relate_t = self.back_tree(eles[0], key)
            choise = 0
            for i,t in enumerate(eles):
                e,ts = self.back_tree(t, key)
                # show(ts, e.name)
                if ts < max_relate_t:
                    
                    choise = i
                    ele = e
                    max_relate_t = ts
            return targets[choise]

        else:
            return targets[0]

    def diff(self, old, new):
        words = old.split()
        news = new.split()
        od = dict()
        nd = dict()
        for i in words:
            od[i] = od.get(i, 0) + 1
        for i in news:
            nd[i] = nd.get(i, 0) + 1

        w = set(od.items())
        w2 = set(nd.items())
        res = len(w2 ^  w)/ len(w2 | w)
        return res


    def _check_if_clicked(self):
        fen = self.diff(self.old_data, self.phantom.page_source)
        # show("diff:",fen, color='red')
        if fen < 0.1:
            return False
        return True

    def switch(self):
        main_window_handle = self.phantom.current_window_handle
        driver.find_element_by_id("ctl00__mainContent_ucObjRegister_btnRegister").click()
        modal_window = None
        while not modal_window:
            for handle in self.phantom.window_handles:
                if handle != main_window_handle:
                    modal_window = handle
                    break

        return modal_window

        


    def finds(self, selectID, fuzzy=None):
        if '[' in selectID and ']' in selectID:
            text = re.findall(r'\[(.+?)\]', selectID)[0]
            loc = re.sub(r'\[(.+?)\]', '', selectID)
            return self.back_recur_finds(loc, text)
            show('find text:',text)
        else:
            selectIDs = selectID.split(">")
            selectID_l = selectIDs[-1]
            target = self.phantom
            for no, SLE in enumerate(selectIDs):
                if SLE == selectID_l:
                    return target.find_elements_by_css_selector(SLE)

                if ':' in SLE:
                    n, i = SLE.split(':')
                    target = target.find_elements_by_css_selector(n)[int(i)]
                else:
                    target = target.find_element_by_css_selector(SLE)


    def find(self, selectID, fuzzy=None):
        if '[' in selectID and ']' in selectID:
            text = re.findall(r'\[(.+?)\]', selectID)[0]
            loc = re.sub(r'\[(.+?)\]', '', selectID)
            return self.back_recur_find(loc, text)
            show('find text:',text)


        selectIDs = selectID.split(">")
        target = self.phantom
        targets = []
        l = len(selectIDs)
        for no, SLE in enumerate(selectIDs):
            try:
                if ':' in SLE:
                    n, i = SLE.split(':')
                    target = target.find_elements_by_css_selector(n)[int(i)]
                else:
                    target = target.find_element_by_css_selector(SLE)
                continue
            except NoSuchElementException as e:
                pass

            try:
                if SLE.startswith("."):
                    if ':' in SLE:
                        n, i = SLE[1:].split(':')
                        # show(n,i)
                        target = target.find_elements_by_class_name(n)[int(i)]
                    else:
                        target = target.find_element_by_class_name(SLE[1:])
                elif SLE.startswith("#"):
                    if ':' in SLE:
                        n, i = SLE[1:].split(':')
                        # show(n,i)
                        target = target.find_elements_by_id(n)[int(i)]
                    else:
                        target = target.find_element_by_id(SLE[1:])
                else:
                    if ':' in SLE:
                        n, i = SLE.split(':')
                        # show(n,i)
                        target = target.find_elements_by_tag_name(n)[int(i)]
                    else:
                        target = target.find_element_by_tag_name(SLE)
            except NoSuchElementException as e:
                show("can not found , continue", e)
                if no == l-1:
                    return 
                continue
        target.source = target.get_attribute('outerHTML')
        return target
    
    def html(self):
        return self.phantom.page_source


    def __call__(self, key, **kargs):
        return self.soup(key, **kargs)

