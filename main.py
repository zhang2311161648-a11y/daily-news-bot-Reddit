import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import feedparser

# 从 GitHub Secrets 中读取你的账号信息
QQ_EMAIL = os.environ.get("QQ_EMAIL")
QQ_AUTH_CODE = os.environ.get("QQ_AUTH_CODE")
RECEIVER_EMAIL = QQ_EMAIL # 默认发给自己，你也可以改成其他邮箱

# 定义你要获取信息的来源 (RSS 源)
FEEDS = {
    "🦷 口腔医学 (Reddit Dentistry)": "https://www.reddit.com/r/Dentistry/.rss",
    "🩺 综合医学 (Reddit Medicine)": "https://www.reddit.com/r/medicine/.rss",
    "🤖 AI 与人工智能 (Reddit MachineLearning)": "https://www.reddit.com/r/MachineLearning/.rss",
    "💻 科技与编程前沿 (Hacker News)": "https://news.ycombinator.com/rss"
}

def fetch_news():
    """抓取 RSS 源的信息并生成 HTML 格式的内容"""
    html_content = "<h2>今日前沿资讯推送 🚀</h2>"
    
    for category, url in FEEDS.items():
        html_content += f"<h3>{category}</h3><ul>"
        try:
            feed = feedparser.parse(url)
            # 每个分类只取前 5 条最新信息，避免邮件太长
            for entry in feed.entries[:5]:
                title = entry.title
                link = entry.link
                html_content += f"<li><a href='{link}'>{title}</a></li>"
        except Exception as e:
            html_content += f"<li>获取失败: {e}</li>"
        html_content += "</ul>"
        
    html_content += "<p><br>由你的专属 GitHub Actions 机器人自动发送 🤖</p>"
    return html_content

def send_email(content):
    """通过 QQ 邮箱的 SMTP 发送邮件"""
    msg = MIMEMultipart()
    msg['From'] = QQ_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = "【每日定制资讯】医学 / 口腔 / AI前沿"

    # 将内容附加为 HTML 格式
    msg.attach(MIMEText(content, 'html', 'utf-8'))

    if not QQ_EMAIL or not QQ_AUTH_CODE:
        print("❌ 致命错误：未获取到 QQ_EMAIL 或 QQ_AUTH_CODE！")
        print("👉 请检查 GitHub 仓库的 Settings -> Secrets and variables -> Actions 中是否正确配置了这两个 Secret。")
        return

    # 清除可能不小心多加的空格
    QQ_EMAIL = QQ_EMAIL.strip()
    QQ_AUTH_CODE = QQ_AUTH_CODE.strip()

    try:
        print(f"正在尝试连接 QQ 邮箱服务器... (发件人: {QQ_EMAIL})")
        server = smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=15)
        server.set_debuglevel(1) # 开启调试输出，打印所有网络交互细节
        print("✅ 连接成功，准备登录...")
        server.login(QQ_EMAIL, QQ_AUTH_CODE)
        print("✅ 登录成功，准备发送...")
        server.sendmail(QQ_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("✅ 邮件发送成功！请检查你的邮箱。")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

if __name__ == "__main__":
    print("开始抓取资讯...")
    news_html = fetch_news()
    print("资讯抓取完成，准备发送邮件...")
    send_email(news_html)
