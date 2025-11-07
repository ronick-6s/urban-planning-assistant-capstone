"""
Report Generator for Urban Planning Assistant
Creates formatted reports from chat history in multiple formats
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import markdown
import jinja2
from cloud_config import get_report_config
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates formatted reports from chat history."""
    
    def __init__(self):
        """Initialize report generator with configuration."""
        self.config = get_report_config()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Setup Jinja2 environment for HTML templates
        self.jinja_env = jinja2.Environment(
            loader=jinja2.DictLoader(self._get_html_templates())
        )
    
    def _setup_custom_styles(self):
        """Setup custom styles for PDF generation."""
        # Custom styles for PDF
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        ))
        
        self.styles.add(ParagraphStyle(
            name='UserMessage',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=10,
            backColor=colors.HexColor('#e3f2fd'),
            borderPadding=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='AssistantMessage',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=10,
            backColor=colors.HexColor('#f8f9fa'),
            borderPadding=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='SystemMessage',
            parent=self.styles['Normal'],
            fontSize=9,
            leftIndent=40,
            rightIndent=40,
            spaceAfter=8,
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica-Oblique'
        ))
    
    def _get_html_templates(self) -> Dict[str, str]:
        """Get HTML templates for report generation."""
        return {
            'base_template': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Urban Planning Assistant Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        
        .header .subtitle {
            margin-top: 10px;
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .metadata {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .metadata table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .metadata td {
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
        }
        
        .metadata td:first-child {
            font-weight: bold;
            color: #666;
            width: 150px;
        }
        
        .chat-history {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .message {
            margin-bottom: 25px;
            padding: 15px;
            border-radius: 8px;
            position: relative;
        }
        
        .message-user {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left: 4px solid #2196f3;
        }
        
        .message-assistant {
            background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
            border-left: 4px solid #9c27b0;
        }
        
        .message-system {
            background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%);
            border-left: 4px solid #ff9800;
            font-style: italic;
        }
        
        .message-header {
            font-weight: bold;
            color: #666;
            font-size: 0.9em;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .message-content {
            color: #333;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .timestamp {
            position: absolute;
            top: 10px;
            right: 15px;
            font-size: 0.8em;
            color: #999;
        }
        
        .footer {
            margin-top: 40px;
            padding: 20px;
            background: #f1f1f1;
            border-radius: 8px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            text-transform: uppercase;
            font-size: 0.8em;
            letter-spacing: 0.5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Urban Planning Assistant</h1>
        <div class="subtitle">Chat History Report</div>
    </div>
    
    <div class="metadata">
        <table>
            <tr><td>User ID:</td><td>{{ user_id }}</td></tr>
            <tr><td>Report Generated:</td><td>{{ timestamp }}</td></tr>
            <tr><td>Report Format:</td><td>{{ format }}</td></tr>
            <tr><td>Chat Duration:</td><td>{{ duration }}</td></tr>
        </table>
    </div>
    
    <div class="stats">
        <div class="stat-item">
            <div class="stat-number">{{ stats.total_messages }}</div>
            <div class="stat-label">Total Messages</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{{ stats.user_messages }}</div>
            <div class="stat-label">User Messages</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{{ stats.assistant_responses }}</div>
            <div class="stat-label">Assistant Responses</div>
        </div>
    </div>
    
    <div class="chat-history">
        <h2>Conversation History</h2>
        {% for message in messages %}
        <div class="message message-{{ message.type }}">
            <div class="message-header">{{ message.sender }}</div>
            {% if message.timestamp %}
            <div class="timestamp">{{ message.timestamp }}</div>
            {% endif %}
            <div class="message-content">{{ message.content }}</div>
        </div>
        {% endfor %}
    </div>
    
    <div class="footer">
        <p>This report was generated by the Urban Planning Assistant system.</p>
        <p>Chennai Smart City Initiative | Generated on {{ timestamp }}</p>
    </div>
</body>
</html>
            '''
        }
    
    def generate_report(self, user_id: str, chat_history: str, 
                       output_format: str = "pdf", 
                       include_metadata: bool = True) -> Tuple[bytes, str]:
        """
        Generate a formatted report from chat history.
        
        Args:
            user_id: ID of the user
            chat_history: Raw chat history text
            output_format: Format for output ('pdf', 'html', 'txt')
            include_metadata: Whether to include metadata
            
        Returns:
            Tuple of (report_content_bytes, filename)
        """
        # Parse chat history
        messages = self._parse_chat_history(chat_history)
        
        # Generate metadata
        metadata = self._generate_metadata(user_id, messages)
        
        # Generate report based on format
        if output_format.lower() == 'pdf':
            content, filename = self._generate_pdf_report(user_id, messages, metadata)
        elif output_format.lower() == 'html':
            content, filename = self._generate_html_report(user_id, messages, metadata)
        else:  # txt
            content, filename = self._generate_text_report(user_id, messages, metadata)
        
        return content, filename
    
    def _parse_chat_history(self, chat_history: str) -> List[Dict[str, Any]]:
        """Parse raw chat history into structured messages."""
        messages = []
        lines = chat_history.split('\n')
        current_message = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for message indicators
            if line.startswith('[USER]'):
                if current_message:
                    messages.append(current_message)
                current_message = {
                    'type': 'user',
                    'sender': 'User',
                    'content': line[6:].strip(),
                    'timestamp': None
                }
            elif line.startswith('[ASSISTANT]'):
                if current_message:
                    messages.append(current_message)
                current_message = {
                    'type': 'assistant',
                    'sender': 'Assistant',
                    'content': line[11:].strip(),
                    'timestamp': None
                }
            elif line.startswith('[SYSTEM]'):
                if current_message:
                    messages.append(current_message)
                current_message = {
                    'type': 'system',
                    'sender': 'System',
                    'content': line[8:].strip(),
                    'timestamp': None
                }
            else:
                # Continue previous message
                if current_message:
                    current_message['content'] += '\n' + line
        
        # Add final message
        if current_message:
            messages.append(current_message)
        
        return messages
    
    def _generate_metadata(self, user_id: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate metadata for the report."""
        now = datetime.now()
        
        user_messages = len([m for m in messages if m['type'] == 'user'])
        assistant_messages = len([m for m in messages if m['type'] == 'assistant'])
        system_messages = len([m for m in messages if m['type'] == 'system'])
        
        return {
            'user_id': user_id,
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
            'total_messages': len(messages),
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'system_messages': system_messages,
            'duration': 'N/A',  # Could be calculated if timestamps were available
            'format': 'PDF/HTML/TXT'
        }
    
    def _generate_pdf_report(self, user_id: str, messages: List[Dict[str, Any]], 
                           metadata: Dict[str, Any]) -> Tuple[bytes, str]:
        """Generate README-style PDF report."""
        from io import BytesIO
        buffer = BytesIO()
        
        # Create PDF document with README-style layout
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=60,
            leftMargin=60,
            topMargin=60,
            bottomMargin=60
        )
        
        # Build README-style story
        story = []
        
        # README-style title with emoji
        title_text = "📋 Urban Planning Studio - Consultation Report"
        story.append(Paragraph(title_text, self.styles['CustomTitle']))
        story.append(Spacer(1, 10))
        
        # Subtitle with metadata
        subtitle_data = [
            [f"Generated: {metadata['timestamp']}"],
            ["System: Urban Planning Assistant"],
            ["Format: Professional README Documentation"]
        ]
        
        subtitle_table = Table(subtitle_data, colWidths=[6*inch])
        subtitle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f6f8fa')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Oblique'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 15)
        ]))
        
        story.append(subtitle_table)
        story.append(Spacer(1, 20))
        
        # Horizontal rule
        story.append(Paragraph("─" * 80, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Report Overview section (README-style table)
        story.append(Paragraph("📊 Report Overview", self.styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Calculate conversation stats
        user_messages = len([m for m in messages if m['type'] == 'user'])
        assistant_messages = len([m for m in messages if m['type'] == 'assistant'])
        total_exchanges = min(user_messages, assistant_messages)
        
        overview_data = [
            ['Attribute', 'Value'],
            ['User ID', f"{metadata['user_id']}"],
            ['Session Date', datetime.now().strftime('%Y-%m-%d')],
            ['Total Interactions', f"{total_exchanges} exchanges"],
            ['Total Messages', str(metadata['total_messages'])],
            ['Report Type', 'Consultation Summary'],
            ['Status', '✅ Complete']
        ]
        
        overview_table = Table(overview_data, colWidths=[2.5*inch, 3.5*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 8)
        ]))
        
        story.append(overview_table)
        story.append(Spacer(1, 20))
        
        # Horizontal rule
        story.append(Paragraph("─" * 80, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Consultation Summary
        story.append(Paragraph("💬 Consultation Summary", self.styles['Heading2']))
        story.append(Spacer(1, 10))
        
        summary_text = "This report documents a comprehensive urban planning consultation session covering sustainable development strategies, community planning solutions, and urban design principles."
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Key Topics Covered
        story.append(Paragraph("🎯 Key Topics Covered", self.styles['Heading3']))
        story.append(Spacer(1, 8))
        
        # Extract topics from user messages
        topics_data = [['Topics Discussed']]
        topic_count = 0
        for message in messages:
            if message['type'] == 'user' and len(message['content']) > 20 and topic_count < 5:
                topic = message['content'][:60].strip()
                if '?' in topic:
                    topic = topic.split('?')[0] + "?"
                topics_data.append([f"✅ {topic}"])
                topic_count += 1
        
        if len(topics_data) > 1:
            topics_table = Table(topics_data, colWidths=[6*inch])
            topics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 1), (-1, -1), 20)
            ]))
            story.append(topics_table)
        
        story.append(Spacer(1, 20))
        
        # Horizontal rule
        story.append(Paragraph("─" * 80, self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Detailed Conversation Log
        story.append(Paragraph("📝 Detailed Conversation Log", self.styles['Heading2']))
        story.append(Spacer(1, 15))
        
        # Process messages into exchanges
        exchange_count = 0
        i = 0
        while i < len(messages):
            if messages[i]['type'] == 'user':
                exchange_count += 1
                user_msg = messages[i]
                
                # Exchange header
                story.append(Paragraph(f"🗣️ Exchange {exchange_count}", self.styles['Heading3']))
                story.append(Spacer(1, 8))
                
                # User query
                query_text = f"<b>Query:</b> <i>\"{user_msg['content'][:150]}{'...' if len(user_msg['content']) > 150 else ''}\"</i>"
                story.append(Paragraph(query_text, self.styles['Normal']))
                story.append(Spacer(1, 8))
                
                # Look for corresponding assistant response
                if i + 1 < len(messages) and messages[i + 1]['type'] == 'assistant':
                    assistant_msg = messages[i + 1]
                    
                    story.append(Paragraph("<b>Response Summary:</b>", self.styles['Normal']))
                    story.append(Spacer(1, 5))
                    
                    # Response content in a styled box
                    response_content = assistant_msg['content'][:400] + ("..." if len(assistant_msg['content']) > 400 else "")
                    story.append(Paragraph(response_content, self.styles['AssistantMessage']))
                    
                    i += 2
                else:
                    i += 1
                
                story.append(Spacer(1, 15))
            else:
                i += 1
        
        # Key Recommendations section
        story.append(Paragraph("─" * 80, self.styles['Normal']))
        story.append(Spacer(1, 15))
        story.append(Paragraph("🎯 Key Recommendations", self.styles['Heading2']))
        story.append(Spacer(1, 10))
        
        recommendations_data = [
            ['Timeline', 'Recommended Actions'],
            ['Immediate (0-6 months)', '☐ Review consultation outcomes\n☐ Identify priority areas\n☐ Engage stakeholders'],
            ['Medium-term (6-18 months)', '☐ Implement strategies\n☐ Monitor progress\n☐ Adjust approaches'],
            ['Long-term (1-5 years)', '☐ Achieve targets\n☐ Integrate solutions\n☐ Share best practices']
        ]
        
        recommendations_table = Table(recommendations_data, colWidths=[2*inch, 4*inch])
        recommendations_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#17a2b8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 8)
        ]))
        
        story.append(recommendations_table)
        story.append(Spacer(1, 20))
        
        # Footer with branding
        story.append(Paragraph("─" * 80, self.styles['Normal']))
        story.append(Spacer(1, 10))
        
        footer_text = """<b>🏙️ Urban Planning Studio</b><br/>
        <i>Intelligent Urban Solutions for Sustainable Communities</i><br/><br/>
        💡 Note: This report represents a comprehensive urban planning consultation session. 
        All recommendations should be adapted to local context, regulations, and community needs."""
        
        story.append(Paragraph(footer_text, self.styles['SystemMessage']))
        
        # Build PDF
        doc.build(story)
        
        # Get content and generate filename
        content = buffer.getvalue()
        buffer.close()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"urban_planning_report_{user_id}_{timestamp}.pdf"
        
        return content, filename
    
    def _generate_html_report(self, user_id: str, messages: List[Dict[str, Any]],
                            metadata: Dict[str, Any]) -> Tuple[bytes, str]:
        """Generate HTML report."""
        template = self.jinja_env.get_template('base_template')
        
        # Prepare data for template
        template_data = {
            'user_id': user_id,
            'timestamp': metadata['timestamp'],
            'format': 'HTML',
            'duration': metadata['duration'],
            'messages': messages,
            'stats': {
                'total_messages': metadata['total_messages'],
                'user_messages': metadata['user_messages'],
                'assistant_responses': metadata['assistant_messages']
            }
        }
        
        # Render HTML
        html_content = template.render(**template_data)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"urban_planning_report_{user_id}_{timestamp}.html"
        
        return html_content.encode('utf-8'), filename
    
    def _generate_text_report(self, user_id: str, messages: List[Dict[str, Any]],
                            metadata: Dict[str, Any]) -> Tuple[bytes, str]:
        """Generate README-style text report."""
        
        # Calculate conversation stats
        user_messages = len([m for m in messages if m['type'] == 'user'])
        assistant_messages = len([m for m in messages if m['type'] == 'assistant'])
        total_exchanges = min(user_messages, assistant_messages)
        
        lines = [
            "# 📋 Urban Planning Studio - Consultation Report",
            "",
            f"> **Generated**: {metadata['timestamp']}  ",
            f"> **System**: Urban Planning Assistant  ",
            f"> **Format**: Professional README Documentation  ",
            "",
            "---",
            "",
            "## 📊 Report Overview",
            "",
            "| Attribute | Value |",
            "|-----------|-------|",
            f"| **User ID** | `{metadata['user_id']}` |",
            f"| **Session Date** | {datetime.now().strftime('%Y-%m-%d')} |",
            f"| **Total Interactions** | `{total_exchanges} exchanges` |",
            f"| **Total Messages** | `{metadata['total_messages']}` |",
            f"| **Report Type** | `Consultation Summary` |",
            f"| **Status** | `✅ Complete` |",
            "",
            "---",
            "",
            "## 💬 Consultation Summary",
            "",
            "This report documents a comprehensive urban planning consultation session covering sustainable development strategies, community planning solutions, and urban design principles.",
            "",
            "### 🎯 Key Topics Covered",
            ""
        ]
        
        # Extract key topics from messages (simplified approach)
        topics_covered = []
        for message in messages:
            if message['type'] == 'user' and len(message['content']) > 20:
                # Extract first part as topic
                topic = message['content'][:80].strip()
                if '?' in topic:
                    topic = topic.split('?')[0] + "?"
                topics_covered.append(f"- ✅ **{topic}**")
        
        lines.extend(topics_covered[:5])  # Limit to 5 topics
        
        lines.extend([
            "",
            "---",
            "",
            "## 📝 Detailed Conversation Log",
            ""
        ])
        
        # Process messages into exchanges
        exchange_count = 0
        i = 0
        while i < len(messages):
            if messages[i]['type'] == 'user':
                exchange_count += 1
                user_msg = messages[i]
                
                lines.extend([
                    f"### 🗣️ Exchange {exchange_count}",
                    "",
                    f"**Query**: *\"{user_msg['content'][:100]}{'...' if len(user_msg['content']) > 100 else ''}\"*",
                    ""
                ])
                
                # Look for corresponding assistant response
                if i + 1 < len(messages) and messages[i + 1]['type'] == 'assistant':
                    assistant_msg = messages[i + 1]
                    
                    lines.extend([
                        "**Response Summary**: ",
                        assistant_msg['content'][:500] + ("..." if len(assistant_msg['content']) > 500 else ""),
                        "",
                        "---",
                        ""
                    ])
                    i += 2
                else:
                    i += 1
            else:
                i += 1
        
        lines.extend([
            "## 🎯 Key Recommendations",
            "",
            "### Immediate Actions (0-6 months)",
            "- [ ] Review consultation outcomes",
            "- [ ] Identify priority implementation areas", 
            "- [ ] Engage relevant stakeholders",
            "- [ ] Develop action timeline",
            "",
            "### Medium-term Goals (6-18 months)",
            "- [ ] Implement recommended strategies",
            "- [ ] Monitor progress and outcomes",
            "- [ ] Adjust approaches based on results",
            "- [ ] Expand successful initiatives",
            "",
            "### Long-term Vision (1-5 years)",
            "- [ ] Achieve sustainable development targets",
            "- [ ] Integrate solutions into comprehensive planning",
            "- [ ] Establish continuous improvement processes",
            "- [ ] Share best practices with other communities",
            "",
            "---",
            "",
            "## 📊 Project Metrics & KPIs",
            "",
            "| Category | Metric | Target |",
            "|----------|--------|--------|",
            "| **Engagement** | Consultation sessions | `Completed` |",
            "| **Planning** | Action items identified | `Multiple` |",
            "| **Implementation** | Priority areas defined | `In Progress` |",
            "| **Outcomes** | Stakeholder satisfaction | `High` |",
            "",
            "---",
            "",
            "## 🔗 Additional Resources",
            "",
            "- 📚 **Urban Planning Best Practices**",
            "- 🌍 **Sustainable Development Guidelines**", 
            "- 🏗️ **Community Engagement Frameworks**",
            "- 💡 **Smart City Innovation Resources**",
            "",
            "---",
            "",
            "## 📞 Next Steps & Contact",
            "",
            "For follow-up consultations or project implementation support:",
            "",
            "- **📧 Email**: Contact through Urban Planning Studio",
            "- **🌐 Platform**: Urban Planning Studio Interface",
            "- **📅 Scheduling**: Available for continued consultation",
            "",
            "---",
            "",
            "> **💡 Note**: This report represents a comprehensive urban planning consultation session. All recommendations should be adapted to local context, regulations, and community needs.",
            "",
            "---",
            "",
            "<div align=\"center\">",
            "",
            "**🏙️ Urban Planning Studio**  ",
            "*Intelligent Urban Solutions for Sustainable Communities*",
            "",
            "[![Built with](https://img.shields.io/badge/Built%20with-Urban%20Planning%20AI-blue)](#)",
            "[![Status](https://img.shields.io/badge/Status-Active%20Consultation-green)](#)", 
            "[![Format](https://img.shields.io/badge/Format-README%20Style-orange)](#)",
            "",
            "</div>"
        ])
        
        content = '\n'.join(lines)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"urban_planning_report_{user_id}_{timestamp}.txt"
        
        return content.encode('utf-8'), filename

# Global instance
report_generator = ReportGenerator()

def generate_chat_report(user_id: str, chat_history: str, 
                        output_format: str = "pdf") -> Tuple[bytes, str]:
    """
    Convenience function to generate a chat history report.
    
    Args:
        user_id: ID of the user
        chat_history: Raw chat history text
        output_format: Format for output ('pdf', 'html', 'txt')
        
    Returns:
        Tuple of (report_content_bytes, filename)
    """
    return report_generator.generate_report(user_id, chat_history, output_format)
