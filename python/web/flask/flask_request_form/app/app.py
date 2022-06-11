from flask import Flask,render_template, url_for, request, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension 
from flask_mail import Mail, Message
from email_validator import validate_email, EmailNotValidError
import logging
import random, string
import os

app = Flask(__name__, static_url_path='')

app.debug = True # ツールバーはDebugモードでのみ起動する

rand_list = [random.choice(string.ascii_letters + string.digits) for i in range(20)]
rand_str = ''.join(rand_list)
app.config["SECRET_KEY"] = rand_str
app.logger.setLevel(logging.DEBUG)
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False # リダイレクトを中断しないようにする
toolbar = DebugToolbarExtension(app)

app.config["MAIL_SERVER"]         = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"]           = os.environ.get("MAIL_PORT")
app.config["MAIL_USE_TLS"]        = os.environ.get("MAIL_USE_TLS")
app.config["MAIL_USERNAME"]       = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"]       = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

mail = Mail(app)

@app.route("/")
def index():
    return "Hello, World!"

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/contact/complete", methods=["GET", "POST"])
def contact_complete():
    if request.method == "POST":
        username      = request.form["username"]
        email        = request.form["email"]
        description  = request.form["description"] 
        
        is_valid:bool = True
        
        if not username:
            flash("ユーザ名は必須です")
            is_valid = False
            
        try:
            validate_email(email)
        except EmailNotValidError:
            flash("メールアドレスの形式で入力してください")
            is_valid = False
            
        if not description:
            flash("問い合わせ内容は必須です")
            is_valid = False
            
        if not is_valid:
            return redirect(url_for("contact"))

        # メールを送る
        send_email(
            email,
            "問い合わせありがとうございました",
            "contact_mail",
            username=username,
            description=description,
        )
        flash("問い合わせありがとうございます")
        return redirect(url_for("contact_complete"))
    
    return render_template("contact_complete.html")

def send_email(to, subject, template, **kwargs):
    msg      = Message(subject, recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
    app.logger.critical("fatal error")
    app.logger.error("error")
    app.logger.warning("warning")
    app.logger.info("info")
    app.logger.debug("debug")