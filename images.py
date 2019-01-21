import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as sl
import tkinter.messagebox as mbox
import requests as rs
import threading, requests, json, re, os
from time import sleep
from lxml import etree
from configparser import ConfigParser

class App(tk.Tk):
    link = False
    status = False
    total = 0
    path = './images/'
    inifile = './Conf.ini'

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

    # 初始化
    def __init__(self):
        super().__init__()

        self.title('图片下载')
        self.geometry('600x480+300+200')
        self.resizable(0, 0)
        # self.iconbitmap()

        self.setup_ui()

    # 设置界面
    def setup_ui(self):

        # Top
        top = ttk.LabelFrame(self, text='链接地址', padding='0 0 0 5')
        top.pack(side=tk.TOP, fill=tk.X, pady=10, padx=5)

        # 输入框
        self.link = tk.StringVar()
        ttk.Entry(top, textvariable=self.link, font=('Arial', 12), width=52).pack(side=tk.LEFT, padx=5)

        # 按钮
        ttk.Button(top, text='粘贴', width=5, command=self.onpaste).pack(side=tk.LEFT)
        ttk.Button(top, text='下载', width=5, command=self.start1).pack(side=tk.RIGHT, padx=5)

        # Middle
        middle = ttk.LabelFrame(self, text='支持', padding='5 0 5 5')
        middle.pack(fill=tk.X, padx=5)

        #
        ttk.Label(middle, text='淘宝,天猫,速卖通,易贝,WISH,1688').pack(side=tk.LEFT)
        ttk.Label(middle, text='作者:QQ519999189').pack(side=tk.RIGHT)

        # 底部 滚动文本
        self.bsText = sl.ScrolledText(self)
        self.bsText.pack(fill=tk.X, padx=5, pady=10)

        # 状态栏
        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status).pack(side=tk.BOTTOM, fill=tk.X, padx=5)
        self.status.set('等待...')

    # 粘贴函数
    def onpaste(self):
        text = self.clipboard_get()
        self.link.set(str(text))

    # 开始
    def start1(self):

        self.total = 0
        self.bsText.delete(1.0, tk.END)
        self.status.set('开始运行...')

        # 创建目录
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        # 设置登陆Cookie
        if not os.path.exists('./Conf.ini'):

            mbox.showerror('系统信息','缺少配置文件')

        conf = ConfigParser()

        conf.read('./Conf.ini')

        if conf.get('path', 'cookie'):

            self.headers['cookie'] = conf.get('path','cookie')

        # 设置线程
        th1 = threading.Thread(target=self.downlod)
        th1.start()

    # 下载
    def downlod(self):

        sites = {}

        sites['amazon'] = r'^https{0,1}://www.amazon.com/'
        sites['tmall'] = r'^https{0,1}://detail.tmall.com/'
        sites['taobao'] = r'^https{0,1}://item.taobao.com/'
        sites['m1688'] = r'^https{0,1}://detail.1688.com/offer/'
        sites['wish'] = r'^https{0,1}://www.wish.com/'
        sites['ebay'] = r'^https{0,1}://www.ebay.com/'
        sites['aliexpress'] = r'^https{0,1}://www.aliexpress.com/'

        for method in sites:

            if re.findall(sites[method], self.link.get().strip(), re.I):
                eval('self.%s()' % method)

                return False

        mbox.showinfo('系统提示', 'Url链接有误!')

    # 下载图片
    def getImages(self, url, name):

        try:

            r = rs.get(url, headers=self.headers)

        except Exception as e:

            mbox.showerror('系统提示', e)

            return False

        with open(name, 'wb') as f:
            f.write(r.content)

        self.bsText.insert(tk.END, '下载完成: %s \n' % url)
        self.bsText.see(tk.END)
        self.status.set('正在下载: %s' % self.total)

    # 天猫下载
    def tmall(self):

        try:
            res = rs.get(self.link.get(), headers=self.headers)

            # 主图信息
            main = re.findall(r'src="(.*?)_60x60q90.jpg"', res.text)


            # 颜色图片信息
            color = re.findall(r'background:url\((.*?)_40x40q90.jpg', res.text)

            # 描述信息
            desc = re.findall(r'"descUrl":"(.*?)",', res.text, re.S)[0]
            url = 'http:%s' % desc
            desc = rs.get(url, headers=self.headers)
            desc = re.findall('="http([^"]*?)\.(gif|jpg|png|jpeg)', desc.text)
            desc = list(set(desc))  # 移除重复值

        except Exception as e:

            mbox.showerror('系统提示re', e)

            return False

        # 颜色图片

        for img in color:

            url = 'https:%s' % img

            self.total += 1

            file = '%scolor_%s%s' % (self.path, self.total, os.path.splitext(url)[1])

            self.getImages(url, file)

            sleep(0.3)

        # 主图片
        for img in main:

            url = 'https:%s' % img

            self.total += 1

            file = '%smain_%s%s' % (self.path, self.total, os.path.splitext(url)[1])

            self.getImages(url, file)

            sleep(0.3)

        # 描述图片
        for img in desc:

            url = 'http%s.%s' % (img[0], img[1])

            self.total += 1

            file = '%sdesc_%s.%s' % (self.path, self.total, img[1])

            self.getImages(url, file)

            sleep(0.3)

        self.status.set('下载完成共计%s张图片' % self.total)

    # 淘宝下载
    def taobao(self):
        try:
            res = rs.get(self.link.get(), headers=self.headers)

            # 主图信息
            main = re.findall(r'src="(.*?)_50x50.jpg"', res.text)

            # 颜色图片信息
            color = re.findall(r'background:url\((.*?)_30x30.jpg', res.text)

            # 描述信息
            desc = re.findall(r"'(//dsc.taobaocdn.com/[^']*?)'\s*:", res.text, re.S)[0]
            url = 'http:%s' % desc
            desc = rs.get(url, headers=self.headers)
            desc = re.findall('="http([^"]*?)\.(gif|jpg|png|jpeg)', desc.text)
            desc = list(set(desc))  # 移除重复值

        except Exception as e:

            mbox.showerror('系统提示re', e)

            return False

        # 颜色图片

        for img in color:
            url = 'https:%s' % img

            self.total += 1

            file = '%scolor_%s%s' % (self.path, self.total, os.path.splitext(url)[1])
            self.getImages(url, file)

            sleep(0.3)

        # 主图片
        for img in main:
            url = 'https:%s' % img

            self.total += 1

            file = '%smain_%s%s' % (self.path, self.total, os.path.splitext(url)[1])

            self.getImages(url, file)

            sleep(0.3)

        # 描述图片
        for img in desc:
            url = 'http%s.%s' % (img[0], img[1])

            self.total += 1

            file = '%sdesc_%s.%s' % (self.path, self.total, img[1])

            self.getImages(url, file)

            sleep(0.3)

        self.status.set('下载完成共计%s张图片' % self.total)

    # 速卖通
    def aliexpress(self):
        try:
            res = rs.get(self.link.get(), headers=self.headers)

            # 主图信息
            main = re.findall(r'src="(.*?)_50x50.jpg"', res.text)

            # 颜色图片信息
            color = re.findall(r'bigpic="(.*?)_640x640.jpg"', res.text)

            # 描述信息
            desc = re.findall(r'detailDesc="([^"]*?)";', res.text, re.S)[0]
            desc = rs.get(desc, headers=self.headers)
            desc = re.findall('="(http[^"]*?)\.(gif|jpg|png|jpeg).*?"', desc.text)
            desc = list(set(desc))  # 移除重复值

        except Exception as e:

            mbox.showerror('系统提示re', e)

            return False


        # 主图片
        for url in main:

            self.total += 1

            file = '%smain_%s%s' % (self.path, self.total, os.path.splitext(url)[1])

            self.getImages(url, file)

            sleep(0.3)

        # 描述图片
        for img in desc:

            url = '%s.%s' % (img[0], img[1])

            self.total += 1

            file = '%sdesc_%s.%s' % (self.path, self.total, img[1])

            self.getImages(url, file)

            sleep(0.3)

        self.status.set('下载完成共计%s张图片' % self.total)

    # WISH
    def wish(self):
        try:
            res = rs.get(self.link.get(), headers=self.headers)

            # 主图信息
            main = re.findall(r'"\d+": "(https.*?)small.jpg"', res.text)
            imag = re.findall(r'"display_picture": "(http.*?)medium.jpg\?cache', res.text)[0]
            main.append(imag)

        except Exception as e:

            mbox.showerror('系统提示re', e)

            return False

        # 主图片
        for url in main:

            self.total += 1

            file = '%smain_%s.jpg' % (self.path, self.total)

            self.getImages(url, file)

            sleep(0.3)

        self.status.set('下载完成共计%s张图片' % self.total)

    # 易贝下载
    def ebay(self):
        try:
            res = rs.get(self.link.get(), headers=self.headers)

            # 主图信息
            main = re.findall(r'"imgArr" : (.*?\])', res.text)[0]
            main = main.replace('\\u002F','/')
            main = json.loads(main)


            # 描述信息
            html = etree.HTML(res.text)
            url  = html.xpath('//iframe[@id="desc_ifr"]/@src')[0]
            desc = rs.get(url, headers=self.headers)
            desc = re.findall('="(http[^"]*?)\.(gif|jpg|png|jpeg)"', desc.text)
            desc = list(set(desc))  # 移除重复值

        except Exception as e:

            mbox.showerror('系统提示re', e)

            return False

        # 主图片
        for img in main:

            url = img.get('maxImageUrl') if img.get('maxImageUrl') else img.get('displayImgUrl')

            self.total += 1

            file = '%smain_%s%s' % (self.path, self.total, os.path.splitext(url)[1])

            self.getImages(url, file)

            sleep(0.3)

        # 描述图片
        for img in desc:
            url = '%s.%s' % (img[0], img[1])

            self.total += 1

            file = '%sdesc_%s.%s' % (self.path, self.total, img[1])

            self.getImages(url, file)

            sleep(0.3)

        self.status.set('下载完成共计%s张图片' % self.total)

    # 1688
    def m1688(self):

        try:

            res = rs.get(self.link.get(), headers=self.headers)

            # 判断是否禁止
            if '1688/淘宝会员（仅限会员名）请在此登录' in res.text:

                mbox.showerror('系统信息','IP被禁止,请添加登录Cookie')
                exit()

            # 主图信息
            main = re.findall(r'original":"(.*?)"', res.text, re.S)

            # 描述信息
            url = re.findall(r'data-tfs-url="(.*?)"', res.text, re.S)[0]

            desc = rs.get(url, headers=self.headers)
            desc = re.findall('"(http[^"]*?)\.(gif|jpg|png|jpeg)', desc.text)
            desc = list(set(desc)) #移除重复值

        except Exception as e:

            mbox.showerror('系统提示re', e)

            return False


        # 主图片
        for url in main:

            self.total += 1

            file = '%smain_%s%s' % (self.path, self.total, os.path.splitext(url)[1])

            self.getImages(url, file)

            sleep(0.3)

        # 描述图片
        for img in desc:

            url = '%s.%s' % (img[0], img[1])

            if url == 'https://assets.alicdn.com/s.gif':

                continue

            self.total += 1

            file = '%sdesc_%s.%s' % (self.path, self.total, img[1])

            self.getImages(url, file)

            sleep(0.3)

        self.status.set('下载完成共计%s张图片' % self.total)


if __name__ == '__main__':
    app = App()

    app.mainloop()
