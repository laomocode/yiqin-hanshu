from pyecharts.charts import Map
from pyecharts import options as opts
from time import strftime,localtime
from fake_useragent import UserAgent
from requests import get
from bs4 import BeautifulSoup
from json import loads
class api:
    def __init__(self,ua=True):
        if ua==True:
            content=get("https://ncov.dxy.cn/ncovh5/view/pneumonia")
        else:
            content=get("https://ncov.dxy.cn/ncovh5/view/pneumonia",headers={"User-Agent":ua})
        content.encoding='utf-8'
        data=content.text
        self.bs = BeautifulSoup(data,'html.parser')
    def guonei(self):
        a=self.bs.find(id="getAreaStat").prettify()
        b=a.replace('<script id="getAreaStat">','')
        a=b.replace('</script>','')
        b=a.replace('}catch(e){}','')
        a=b.replace(' try { window.getAreaStat = ','')
        return loads(a)
    def data(self):
        a=self.bs.find(id="getStatisticsService").prettify()
        b=a.replace('<script id="getStatisticsService">','')
        a=b.replace('</script>','')
        b=a.replace('}catch(e){}','')
        a=b.replace(' try { window.getStatisticsService = ','')
        return loads(a)
def main_handler(event, context):
    global api
    geo=Map(init_opts=opts.InitOpts(page_title="国内疫情地图",js_host="https://js.yiqin.zw2s.ltd/"))
    ua=UserAgent()
    api=api(ua=ua.random)
    data=api.guonei()
    data2=api.data()
    updatetime=strftime("%Y-%m-%d %H:%M:%S",localtime(data2['modifyTime']/1000))
    zhongdata=[]
    for a in range(len(data)):
        tempdata=[]
        tempdata.append(data[a]['provinceShortName'])
        tempdata.append(data[a]['currentConfirmedCount'])
        zhongdata.append(tempdata)
    pingjun=data2['currentConfirmedCount']/len(data)
    geo.set_global_opts(title_opts=opts.TitleOpts(title="国内疫情地图",subtitle="目前共确诊"+str(data2['currentConfirmedCount'])+"例，数据来自丁香园，截止时间："+updatetime),visualmap_opts=opts.VisualMapOpts(max_=pingjun),legend_opts=opts.LegendOpts(is_show=False))
    geo.add("确诊",zhongdata, maptype="china")
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {'Content-Type': 'text/html; charset=utf-8'},
        "body": geo.render_embed()
    }