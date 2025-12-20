# -*- coding: utf-8 -*-
"""
LLM Message Generation Service
Generates cute, varied messages for baby alerts using Claude
"""
import os
from typing import Optional
from anthropic import Anthropic


def format_time_since(hours: float) -> str:
    """
    Convert decimal hours to a nice Hebrew string, rounded to nearest 5 minutes
    Examples:
        3.25 -> "3 שעות ורבע"
        2.5 -> "שעתיים וחצי"
        1.75 -> "שעה ושלושת רבעים"
        0.5 -> "חצי שעה"
        1.1167 -> "שעה ו-10 דקות" (rounded from 1:07)
        3.1 -> "3 שעות ו-5 דקות" (rounded from 3:06)
    """
    total_minutes = int(hours * 60)

    # Round to nearest 5 minutes
    total_minutes = round(total_minutes / 5) * 5

    h = total_minutes // 60
    m = total_minutes % 60

    if hours < 1:
        # Less than an hour - show only minutes
        if m == 0:
            return "כמה דקות"
        elif m == 30:
            return "חצי שעה"
        elif m == 15:
            return "רבע שעה"
        elif m == 45:
            return "שלושת רבעים של שעה"
        else:
            return f"{m} דקות"

    # Build hour part
    if h == 1:
        hour_text = "שעה"
    elif h == 2:
        hour_text = "שעתיים"
    else:
        hour_text = f"{h} שעות"

    # Build minute part
    if m == 0:
        return hour_text
    elif m == 30:
        return f"{hour_text} וחצי"
    elif m == 15:
        return f"{hour_text} ורבע"
    elif m == 45:
        return f"{hour_text} ושלושת רבעים"
    elif m == 5:
        return f"{hour_text} וחמש דקות"
    elif m == 10:
        return f"{hour_text} ועשר דקות"
    elif m == 20:
        return f"{hour_text} ועשרים דקות"
    elif m == 25:
        return f"{hour_text} ועשרים וחמש דקות"
    elif m == 35:
        return f"{hour_text} ושלושים וחמש דקות"
    elif m == 40:
        return f"{hour_text} וארבעים דקות"
    elif m == 50:
        return f"{hour_text} וחמישים דקות"
    elif m == 55:
        return f"{hour_text} וחמישים וחמש דקות"
    else:
        return f"{hour_text} ו-{m} דקות"


class CuteMessageGenerator:
    """Generate cute, personalized alert messages using Claude"""

    def __init__(self):
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.client = None
        if self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
            except Exception:
                self.client = None

    def is_available(self) -> bool:
        """Check if LLM service is configured and available"""
        return self.client is not None

    def generate_daily_summary(
        self,
        child_name: str,
        summary_data: dict,
        date_str: str,
        use_llm: bool = True
    ) -> str:
        """
        Generate a cute daily summary message

        Args:
            child_name: The child's name
            summary_data: Dict with summary data (feedings, sleep, diapers)
            date_str: Date string for the summary
            use_llm: Whether to use LLM (if False or unavailable, uses fallback)

        Returns:
            A cute, personalized summary message
        """
        if not use_llm or not self.is_available():
            return self._get_fallback_summary(child_name, summary_data, date_str)

        try:
            prompt = self._build_summary_prompt(child_name, summary_data, date_str)

            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=400,
                temperature=1.0,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return message.content[0].text.strip()

        except Exception:
            return self._get_fallback_summary(child_name, summary_data, date_str)

    def generate_alert_message(
        self,
        child_name: str,
        alert_type: str,
        details: dict,
        use_llm: bool = True
    ) -> str:
        """
        Generate a cute alert message

        Args:
            child_name: The child's name
            alert_type: Type of alert (feeding_overdue, overtired, diaper_overdue, medication_due)
            details: Dict with alert details (minutes_overdue, hours_since, etc.)
            use_llm: Whether to use LLM (if False or unavailable, uses fallback)

        Returns:
            A cute, personalized message string
        """
        if not use_llm or not self.is_available():
            return self._get_fallback_message(child_name, alert_type, details)

        try:
            prompt = self._build_prompt(child_name, alert_type, details)

            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=150,
                temperature=1.0,  # More creative/varied
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return message.content[0].text.strip()

        except Exception:
            # Fallback on any error
            return self._get_fallback_message(child_name, alert_type, details)

    def _build_prompt(self, child_name: str, alert_type: str, details: dict) -> str:
        """Build prompt for Claude"""

        whatsapp_format_instructions = """
עצב את ההודעה בפורמט WhatsApp markdown:
- השתמש ב-*טקסט מודגש* להדגשה (מילות מפתח חשובות)
- השתמש ב-_טקסט נטוי_ לדברים משניים או חמודים
- השתמש באימוג'ים רלוונטיים בתחילת משפטים או במקומות מתאימים
- הפרד בין חלקים עם שורה ריקה אם צריך

דוגמה לעיצוב טוב:
🍼 *נעמי רעבה מאוד!*
עברו כבר _45 דקות_ מאז האכלה אחרונה 😋

הודעה צריכה להיות קצרה (2-3 שורות מקסימום), חמודה, ומעוצבת יפה."""

        if alert_type == 'feeding_overdue':
            minutes = details.get('minutes_overdue', 0)
            return f"""כתוב הודעת התראה חמודה בעברית ש*{child_name}* רעבה.
איחור של {minutes} דקות מהאכלה.

{whatsapp_format_instructions}

תהיה יצירתי ושנה את הסגנון בכל פעם (חמוד, מצחיק, דרמטי קצת, עדין).
רק את ההודעה המעוצבת, בלי הסברים."""

        elif alert_type == 'overtired':
            minutes = details.get('minutes_awake', 0)
            return f"""כתוב הודעת התראה חמודה בעברית ש*{child_name}* עייפה מאוד.
ערה כבר {minutes} דקות.

{whatsapp_format_instructions}

תהיה יצירתי ושנה את הסגנון בכל פעם (חמוד, מצחיק, דרמטי קצת, עדין).
רק את ההודעה המעוצבת, בלי הסברים."""

        elif alert_type == 'diaper_overdue':
            hours = details.get('hours_since', 0)
            time_text = format_time_since(hours)
            return f"""כתוב הודעת התראה חמודה בעברית שזמן להחליף חיתול ל*{child_name}*.
עברו {time_text} מחיתול אחרון.

{whatsapp_format_instructions}

תהיה יצירתי ושנה את הסגנון בכל פעם (חמוד, מצחיק, דרמטי קצת, עדין).
רק את ההודעה המעוצבת, בלי הסברים."""

        elif alert_type == 'medication_due':
            med_name = details.get('medication', {}).get('name', 'תרופה')
            dosage = details.get('medication', {}).get('dosage', '')
            minutes_until = details.get('minutes_until', 0)

            if minutes_until < 0:
                status = f"באיחור של {abs(minutes_until)} דקות"
            else:
                status = f"בעוד {minutes_until} דקות"

            return f"""כתוב הודעת תזכורת חמודה בעברית לתת תרופה ל*{child_name}*.
תרופה: {med_name} {dosage}
זמן: {status}

{whatsapp_format_instructions}

תהיה יצירתי ושנה את הסגנון בכל פעם (חמוד, מצחיק, דרמטי קצת, עדין).
רק את ההודעה המעוצבת, בלי הסברים."""

        return ""

    def _build_summary_prompt(self, child_name: str, summary_data: dict, date_str: str) -> str:
        """Build prompt for daily summary"""

        feedings = summary_data.get('feedings', {})
        sleep = summary_data.get('sleep', {})
        diapers = summary_data.get('diapers', {})

        return f"""כתוב סיכום יומי חמוד ומצחיק בעברית על היום של *{child_name}*.

📅 התאריך: {date_str}

הנתונים:
🍼 האכלות: {feedings.get('count', 0)} פעמים, סה"כ {feedings.get('total_duration_minutes', 0):.0f} דקות{f", {feedings.get('total_amount', 0):.0f} ml" if feedings.get('total_amount') else ""}
💤 שינה: {sleep.get('count', 0)} תקופות, סה"כ {sleep.get('total_duration_hours', 0):.1f} שעות ({sleep.get('naps', 0)} תנומות)
🧷 חיתולים: {diapers.get('count', 0)} פעמים

עצב את ההודעה בפורמט WhatsApp markdown:
- השתמש ב-*טקסט מודגש* להדגשת כותרות
- השתמש ב-_טקסט נטוי_ למספרים וסטטיסטיקות
- השתמש באימוג'ים רלוונטיים
- הפרד בין חלקים עם שורה ריקה

סגנון:
- תהיה חמוד ומצחיק
- תן סיכום כללי קצר על היום (שורה אחת)
- הצג את הסטטיסטיקות בצורה יפה ומסודרת
- הוסף הערה קצרה וחמודה בסוף
- 6-8 שורות מקסימום

דוגמה לסגנון:
📊 *סיכום יום של נעמי*
יום מקסים! הרבה אכילה, שינה טובה 💕

🍼 _7 האכלות_ | 120 דקות
💤 _5 תקופות שינה_ | 11.5 שעות
🧷 _6 חיתולים_

ממשיכים חזק! 💪✨

רק את ההודעה המעוצבת, בלי הסברים."""

    def _get_fallback_message(self, child_name: str, alert_type: str, details: dict) -> str:
        """Fallback messages when LLM is not available - formatted for WhatsApp"""

        if alert_type == 'feeding_overdue':
            minutes = details.get('minutes_overdue', 0)
            return f"""🍼 *{child_name} רעבה!*
עברו כבר _{minutes} דקות_ מאז האכלה אחרונה 😋"""

        elif alert_type == 'overtired':
            minutes = details.get('minutes_awake', 0)
            return f"""💤 *{child_name} עייפה מאוד!*
ערה כבר _{minutes} דקות_ - זמן לישון 😴"""

        elif alert_type == 'diaper_overdue':
            hours = details.get('hours_since', 0)
            time_text = format_time_since(hours)
            return f"""🧷 *זמן לחיתול!*
עברו _{time_text}_ מחיתול אחרון 👶"""

        elif alert_type == 'medication_due':
            med_name = details.get('medication', {}).get('name', 'תרופה')
            dosage = details.get('medication', {}).get('dosage', '')
            minutes_until = details.get('minutes_until', 0)

            if minutes_until < 0:
                return f"""💊 *זמן לתרופה!*
*{med_name}* {dosage}
באיחור של _{abs(minutes_until)} דקות_ ⚠️"""
            else:
                return f"""💊 *תזכורת תרופה*
*{med_name}* {dosage}
בעוד _{minutes_until} דקות_ 🕐"""

        return f"*התראה עבור {child_name}*"

    def _get_fallback_summary(self, child_name: str, summary_data: dict, date_str: str) -> str:
        """Fallback summary when LLM is not available - formatted for WhatsApp"""

        feedings = summary_data.get('feedings', {})
        sleep = summary_data.get('sleep', {})
        diapers = summary_data.get('diapers', {})

        message = f"""📊 *סיכום יום של {child_name}*
📅 {date_str}

🍼 *האכלות:* _{feedings.get('count', 0)} פעמים_"""

        if feedings.get('total_amount'):
            message += f" | {feedings.get('total_amount', 0):.0f} ml"

        message += f"""

💤 *שינה:* _{sleep.get('total_duration_hours', 0):.1f} שעות_
({sleep.get('naps', 0)} תנומות)

🧷 *חיתולים:* _{diapers.get('count', 0)} פעמים_

יום מקסים! 💕"""

        return message


# Global singleton
_message_generator = None

def get_message_generator() -> CuteMessageGenerator:
    """Get or create the global message generator instance"""
    global _message_generator
    if _message_generator is None:
        _message_generator = CuteMessageGenerator()
    return _message_generator
