from io import BytesIO
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
from models.queries.report import fetch_app_usage_and_activity

def format_time(seconds):
    if seconds == 0:
        return "0 secs"
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}m {seconds}s"

def generate_report(app_logs):
    apps = []
    top_apps_raw = []
    concerns = []
    focus_scores = {}
    score_sum = 0
    score_count = 0

    for app in app_logs:
        name = app['app_name']
        focused = app['usage_focused_time']
        background = app['background_time']
        activity = app['activity_focused_time']

        # Add formatted data for 'apps'
        apps.append({
            'app_name': name,
            'usage_focused_time': f"{format_time(focused)}",
            'background_time': f"{format_time(background)}",
            'activity_focused_time': f"{format_time(activity)}"
        })

        # Track for top apps
        top_apps_raw.append({'app_name': name, 'focused_time': focused})

        # Concerns
        if focused == 0:
            concerns.append(f"{name} has zero focused time, might be a distraction or misused.")
        if background > 3600:
            concerns.append(f"{name} is running in the background for too long.")
        if focused > 0 and activity / focused < 0.3:
            concerns.append(f"{name} has very low activity time. Could be passive usage.")

        # Focus score
        total_time = focused + background + 1  # to avoid division by zero
        score = round((focused + activity) / total_time * 100, 2)
        focus_scores[name] = score
        score_sum += score
        score_count += 1

    # Top apps (sorted)
    top_apps = sorted(top_apps_raw, key=lambda x: x['focused_time'], reverse=True)[:3]

    # Final score (average of all focus scores)
    final_score = round(score_sum / score_count) if score_count else 0

    return {
        'apps': apps,
        'top_apps': top_apps,
        'concerns': concerns,
        'focus_scores': focus_scores,
        'final_score': final_score
    }


def generate_pdf(report_data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.darkolivegreen)
    c.drawString(50, 730, "📊 Focus Report:")
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.olivedrab)
    c.drawRightString(width - 50, 690, f"Score: {report_data['final_score']} / 100")
    
    c.setFont("Helvetica", 18)
    c.setFillColor(colors.black)
    c.drawString(55, 690, "Date: "+ str(datetime.today()))
    

    y_position = 660

    # Table Headers
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.setStrokeColor(colors.black)
    c.drawString(55, y_position, "App")
    c.drawString(180, y_position, "Focused Time")
    c.drawString(330, y_position, "Background Time")
    c.drawString(470, y_position, "Activity Time")

    y_position -= 30
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)

    for app in report_data['apps']:
        c.setStrokeColor(colors.black)
        c.drawString(55, y_position, app['app_name'].title())
        c.drawString(180, y_position, app['usage_focused_time'])
        c.drawString(330, y_position, app['background_time'])
        c.drawString(470, y_position, app['activity_focused_time'])
        y_position -= 25

        if y_position < 100:
            c.showPage()
            y_position = 750

    # Section: Top 3 Apps
    y_position -= 20
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.black)
    c.drawString(50, y_position, "⭐ Top 3 App Usage (Based on Focused Time):")
    y_position -= 25
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)

    for idx, app in enumerate(report_data['top_apps'], start=1):
        c.drawString(60, y_position, f"{idx}. {app['app_name'].title()}: {app['focused_time']} seconds")
        y_position -= 18

    # Section: Concerns or Lookouts
    y_position -= 15
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.black)
    c.drawString(50, y_position, "⚠️ Concerns or Lookouts:")
    y_position -= 25
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)

    for concern in report_data['concerns']:
        c.drawString(60, y_position, f"• {concern}")
        y_position -= 18

        if y_position < 100:
            c.showPage()
            y_position = 750

    # Section: Focus Scores
    y_position -= 10
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.black)
    c.drawString(50, y_position, "🎯 Focus Scores:")
    y_position -= 25
    c.setFont("Helvetica", 13)
    c.setFillColor(colors.black)

    for app, score in report_data['focus_scores'].items():
        c.drawString(60, y_position, f"{app.title()}: {score:.2f}%")
        y_position -= 18

        if y_position < 100:
            c.showPage()
            y_position = 750

    

    c.save()
    buffer.seek(0)
    return buffer

date = datetime.today()
report_data = fetch_app_usage_and_activity(date)
report_data = generate_report(report_data)
# Generate the PDF
pdf_buffer = generate_pdf(report_data)

# Get user's Downloads folder
downloads_path = str(Path.home() / "Downloads")
filename = f"usage_report_{date}.pdf"
pdf_path = os.path.join(downloads_path, filename)


# You can save the PDF to a file like this:
with open(pdf_path, "wb") as f:
    f.write(pdf_buffer.read())
