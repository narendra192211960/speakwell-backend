cards = [
    {'name': 'Basic Vowel Sounds', 'tag': 'vowels', 'tint': '#2E86DE', 'bg': '#e0e7ff', 'emoji': '🔊', 'title_html': 'Basic Vowel<br>Sounds'},
    {'name': 'Simple Words - Daily Life', 'tag': 'words', 'tint': '#27AE60', 'bg': '#dcfce7', 'emoji': '💬', 'title_html': 'Simple<br>Words'},
    {'name': 'Numbers 1-10', 'tag': 'numbers', 'tint': '#8E44AD', 'bg': '#f3e8ff', 'emoji': '🔢', 'title_html': 'Numbers<br>1–10'},
    {'name': 'R and L Sounds', 'tag': 'consonants', 'tint': '#E67E22', 'bg': '#ffedd5', 'emoji': '👂', 'title_html': 'R and L<br>Sounds'},
    {'name': 'Self Exercise', 'tag': 'self_exercise', 'tint': '#E74C3C', 'bg': '#fee2e2', 'emoji': '🎤', 'title_html': 'Self<br>Exercise'},
    {'name': 'Paragraph Reading', 'tag': 'paragraphs', 'tint': '#16A085', 'bg': '#ccfbf1', 'emoji': '📄', 'title_html': 'Paragraph<br>Reading'},
    {'name': 'Short Sentences', 'tag': 'sentences', 'tint': '#3498DB', 'bg': '#e0f2fe', 'emoji': '📝', 'title_html': 'Short<br>Sentences'},
    {'name': 'TH Sound Practice', 'tag': 'consonants', 'tint': '#D35400', 'bg': '#ffebd6', 'emoji': '📢', 'title_html': 'TH Sound<br>Practice'},
    {'name': 'Tongue Twisters', 'tag': 'fluency', 'tint': '#9B59B6', 'bg': '#f3e8ff', 'emoji': '📈', 'title_html': 'Tongue<br>Twisters'},
    {'name': 'Medical Terminology', 'tag': 'words', 'tint': '#C0392B', 'bg': '#ffe4e6', 'emoji': '❤️', 'title_html': 'Medical<br>Terminology'},
    {'name': 'Complex Sentences', 'tag': 'sentences', 'tint': '#3498DB', 'bg': '#e0f2fe', 'emoji': '📚', 'title_html': 'Complex<br>Sentences'}
]

html = ""
for i, c in enumerate(cards):
    html += f'''            <div class="exercise-card glass-card" data-category="{c['tag']}" onclick="startCategory('{c['tag']}')" style="cursor:pointer; display:flex; flex-direction:column; align-items:center; text-align:center; padding: 24px; gap: 8px; border: 1px solid rgba(0,0,0,0.05); border-radius: 20px;">
                <div style="background:{c['bg']}; color:{c['tint']}; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; margin-bottom: 8px;">
                    {c['emoji']}
                </div>
                <h3 style="font-size: 1.1rem; font-weight: 800; color: var(--primary-dark); line-height: 1.2; height: 2.4em; display: flex; align-items: center; justify-content: center;">{c['title_html']}</h3>
                <div style="margin-top: 8px; font-size: 0.9rem; font-weight: 700; color: {c['tint']};" class="stat-accuracy" data-ex="{c['name']}">Avg Accuracy: 0%</div>
                <div style="font-size: 0.8rem; color: {c['tint']}; margin-bottom: 16px;" class="stat-words" data-ex="{c['name']}">Words Practiced: 0</div>
                <div style="background:{c['tint']}; color:white; width: 100%; padding: 12px; border-radius: 12px; font-weight: 800; margin-top: auto; transition: opacity 0.2s;">Start</div>
            </div>\n'''

with open('c:/Users/ambat/AndroidStudioProjects/speakwell/website/html/training_cards.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done!")
