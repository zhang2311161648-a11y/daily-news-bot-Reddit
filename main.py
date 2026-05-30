import os
import re
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
    "💻 科技与编程前沿 (Hacker News)": "https://news.ycombinator.com/rss",
    "👗 时尚与潮流 (Reddit Fashion)": "https://www.reddit.com/r/fashion/.rss"
}

def clean_html_and_text(raw_html):
    """去除 HTML 标签并清理无用文本"""
    # 移除 HTML 标签
    cleanr = re.compile('<.*?>')
    text = re.sub(cleanr, '', raw_html)
    # Reddit 的摘要里经常包含 "submitted by" 或 "[link] [comments]"，我们简单清理一下
    text = text.replace("[link]", "").replace("[comments]", "").strip()
    return text

def fetch_news():
    """抓取 RSS 源的信息并生成 HTML 格式的内容"""
    html_content = "<div style='font-family: sans-serif;'>"
    html_content += "<h2>今日前沿资讯推送 🚀</h2>"
    
    for category, url in FEEDS.items():
        html_content += f"<h3 style='color: #333; border-bottom: 1px solid #eee; padding-bottom: 5px;'>{category}</h3><ul style='list-style-type: none; padding-left: 0;'>"
        try:
            feed = feedparser.parse(url)
            # 每个分类只取前 5 条最新信息
            for entry in feed.entries[:5]:
                title = entry.title
                link = entry.link
                
                # 尝试提取文章的 summary 或 description
                summary = getattr(entry, 'summary', getattr(entry, 'description', ''))
                clean_summary = clean_html_and_text(summary)
                
                # 截取前 150 个字符作为摘要
                if len(clean_summary) > 150:
                    clean_summary = clean_summary[:150] + "..."
                elif len(clean_summary) == 0:
                    clean_summary = "暂无内容摘要。"
                    
                # 组装这篇帖子的 HTML
                html_content += f"<li style='margin-bottom: 18px;'>"
                html_content += f"<a href='{link}' style='font-size: 16px; font-weight: bold; text-decoration: none; color: #1a0dab;'>{title}</a>"
                html_content += f"<div style='font-size: 13px; color: #666; margin-top: 4px; line-height: 1.5;'>{clean_summary}</div>"
                html_content += f"</li>"
        except Exception as e:
            html_content += f"<li>获取失败: {e}</li>"
        html_content += "</ul>"
        
    html_content += "<p style='color: #999; font-size: 12px; text-align: center; margin-top: 30px;'>由你的专属 GitHub Actions 机器人自动发送 🤖</p>"
    html_content += "</div>"
    return html_content

def send_email(content):
    """通过 QQ 邮箱的 SMTP 发送邮件"""
    if not QQ_EMAIL or not QQ_AUTH_CODE:
        print("❌ 致命错误：未获取到 QQ_EMAIL 或 QQ_AUTH_CODE！")
        return

    # 清除可能多加的空格，并存入局部变量
    clean_qq_email = QQ_EMAIL.strip()
    clean_qq_auth_code = QQ_AUTH_CODE.strip()

    msg = MIMEMultipart()
    msg['From'] = clean_qq_email
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = "【每日定制资讯】医学 / 口腔 / AI前沿"

    # 将内容附加为 HTML 格式
    msg.attach(MIMEText(content, 'html', 'utf-8'))

    try:
        print(f"正在尝试连接 QQ 邮箱服务器... (发件人: {clean_qq_email})")
        server = smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=15)
        server.set_debuglevel(1) # 开启调试输出
        print("✅ 连接成功，准备登录...")
        server.login(clean_qq_email, clean_qq_auth_code)
        print("✅ 登录成功，准备发送...")
        server.sendmail(clean_qq_email, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("✅ 邮件发送成功！请检查你的邮箱。")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

if __name__ == "__main__":
    print("开始抓取资讯...")
    news_html = fetch_news()
    print("资讯抓取完成，准备发送邮件...")
    send_email(news_html)
