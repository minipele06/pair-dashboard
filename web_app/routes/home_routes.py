from flask import Blueprint, render_template, Response, request, redirect, flash, session
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import base64

#load functions from app
from app.price import pricefind
from app.price import stockinfo
from app.price import tstatcalc
from app.price import sharpe

#create page directory
home_routes = Blueprint("home_routes", __name__)

@home_routes.route("/", methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template("home.html")
    else:
        info = dict(request.form)
        try:
            lentry = info['lentry']
            sentry = info['sentry']
            mhp = info['mhp']
            sdate = info['sdate']
            edate = info['edate']
            symbol = info['ticker'].upper()
            symbol2 = info['ticker2'].upper()
            df = pricefind(symbol)
            df2 = pricefind(symbol2)
            name = stockinfo(symbol)
            name2 = stockinfo(symbol2)
            results = df[(df['Date'] >= sdate) & (df['Date'] <= edate)]
            results2 = df2[(df2['Date'] >= sdate) & (df2['Date'] <= edate)]
            tstat = abs(tstatcalc(results,results2))
            sharpe = sharpe(results,results2,lentry,sentry,mhp)
            if tstat >= 3.43:
                check = "Stationary at 2%"
            elif tstat >= 3.12:
                check = "Stationary at 5%"
            elif tstat >= 2.57:
                check = "Stationary at 10%"
            else:
                check = "Non-stationary"
            fig = Figure()
            axis = fig.add_subplot(1, 1, 1)
            axis.set_xlabel("Date")
            axis.set_ylabel("Spread")
            axis.grid()
            axis.plot(results2['Date'], results2['Diff'], label=f"{symbol2} - {symbol}", linestyle="--", color="b")
            axis.legend(bbox_to_anchor=(0.2, 1.0))
            # Convert plot to PNG image
            pngImage = io.BytesIO()
            FigureCanvas(fig).print_png(pngImage)

            # Encode PNG image to base64 string
            pngImageB64String = "data:image/png;base64,"
            pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
            results2.drop(columns=['Diff','Delta'],axis=1,inplace=True)
            results = results.to_dict('records')
            results2 = results2.to_dict('records')
            tbd='TBD'
            return render_template("home.html", results=results, results2=results2, name=name,name2=name2, sdate=sdate,edate=edate,symbol=symbol,symbol2=symbol2, check=check,image=pngImageB64String,lt=lentry,st=sentry,mhp=mhp,sharpe=sharpe)
        except KeyError:
            sdate = info['sdate']
            edate = info['edate']
            symbol = info['ticker'].upper()
            symbol2 = info['ticker2'].upper()
            df = pricefind(symbol)
            df2 = pricefind(symbol2)
            name = stockinfo(symbol)
            name2 = stockinfo(symbol2)
            results = df[(df['Date'] >= sdate) & (df['Date'] <= edate)]
            results2 = df2[(df2['Date'] >= sdate) & (df2['Date'] <= edate)]
            tstat = abs(tstatcalc(results,results2))
            if tstat >= 3.43:
                check = "Stationary at 2%"
            elif tstat >= 3.12:
                check = "Stationary at 5%"
            elif tstat >= 2.57:
                check = "Stationary at 10%"
            else:
                check = "Non-stationary"
            fig = Figure()
            axis = fig.add_subplot(1, 1, 1)
            axis.set_xlabel("Date")
            axis.set_ylabel("Spread")
            axis.grid()
            axis.plot(results2['Date'], results2['Diff'], label=f"{symbol2} - {symbol}", linestyle="--", color="b")
            axis.legend(bbox_to_anchor=(0.2, 1.0))
            # Convert plot to PNG image
            pngImage = io.BytesIO()
            FigureCanvas(fig).print_png(pngImage)

            # Encode PNG image to base64 string
            pngImageB64String = "data:image/png;base64,"
            pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
            results2.drop(columns=['Diff','Delta'],axis=1,inplace=True)
            results = results.to_dict('records')
            results2 = results2.to_dict('records')
            tbd='TBD'
            return render_template("home.html", results=results, results2=results2, name=name,name2=name2, sdate=sdate,edate=edate,symbol=symbol,symbol2=symbol2, check=check,image=pngImageB64String,lt=tbd,st=tbd,mhp=tbd,sharpe=tbd)