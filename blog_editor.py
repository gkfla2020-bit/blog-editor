"""
Blog Post Editor with Live Preview
마크다운으로 글 쓰면서 실시간 미리보기
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import markdown
import webbrowser
import tempfile
import os
import shutil
import base64
from datetime import datetime
from tkinterdnd2 import DND_FILES, TkinterDnD

class BlogEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Blog Post Editor")
        self.root.geometry("1400x800")
        self.root.configure(bg='#1a1a1a')
        
        # Temp file for preview
        self.temp_html = None
        # Image storage folder
        self.images_folder = os.path.join(os.path.dirname(__file__), 'post_images')
        os.makedirs(self.images_folder, exist_ok=True)
        self.images = []  # List of image paths used in post
        
        self.setup_ui()
        self.setup_drag_drop()
        self.update_preview()
    
    def setup_ui(self):
        # Main container
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Style
        style = ttk.Style()
        style.configure('Dark.TFrame', background='#1a1a1a')
        style.configure('Dark.TLabel', background='#1a1a1a', foreground='#888', font=('Arial', 9))
        style.configure('Dark.TEntry', fieldbackground='#333', foreground='#fff')
        
        # Top: Meta inputs
        meta_frame = tk.Frame(main, bg='#252525', pady=10, padx=15)
        meta_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(meta_frame, text="POST EDITOR", bg='#252525', fg='#666', 
                font=('Arial', 8, 'bold')).pack(anchor='w')
        
        inputs_frame = tk.Frame(meta_frame, bg='#252525')
        inputs_frame.pack(fill=tk.X, pady=(8, 0))
        
        # Title
        tk.Label(inputs_frame, text="Title:", bg='#252525', fg='#888', 
                font=('Arial', 9)).pack(side=tk.LEFT)
        self.title_var = tk.StringVar()
        self.title_entry = tk.Entry(inputs_frame, textvariable=self.title_var, 
                                   bg='#333', fg='#fff', insertbackground='#fff',
                                   font=('Arial', 11), width=40, relief='flat', bd=5)
        self.title_entry.pack(side=tk.LEFT, padx=(5, 20))
        self.title_var.trace('w', lambda *args: self.update_preview())
        
        # Date
        tk.Label(inputs_frame, text="Date:", bg='#252525', fg='#888',
                font=('Arial', 9)).pack(side=tk.LEFT)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.date_entry = tk.Entry(inputs_frame, textvariable=self.date_var,
                                  bg='#333', fg='#fff', insertbackground='#fff',
                                  font=('Arial', 11), width=12, relief='flat', bd=5)
        self.date_entry.pack(side=tk.LEFT, padx=(5, 20))
        self.date_var.trace('w', lambda *args: self.update_preview())
        
        # Category
        tk.Label(inputs_frame, text="Category:", bg='#252525', fg='#888',
                font=('Arial', 9)).pack(side=tk.LEFT)
        self.category_var = tk.StringVar(value='Research')
        self.category_entry = tk.Entry(inputs_frame, textvariable=self.category_var,
                                      bg='#333', fg='#fff', insertbackground='#fff',
                                      font=('Arial', 11), width=15, relief='flat', bd=5)
        self.category_entry.pack(side=tk.LEFT, padx=(5, 20))
        self.category_var.trace('w', lambda *args: self.update_preview())
        
        # Buttons
        btn_frame = tk.Frame(inputs_frame, bg='#252525')
        btn_frame.pack(side=tk.RIGHT)
        
        tk.Button(btn_frame, text="Preview in Browser", command=self.preview_browser,
                 bg='#444', fg='#fff', font=('Arial', 9), relief='flat', padx=15, pady=5,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Save HTML", command=self.save_html,
                 bg='#0080c6', fg='#fff', font=('Arial', 9, 'bold'), relief='flat', padx=15, pady=5,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Split pane: Editor | Preview
        paned = tk.PanedWindow(main, orient=tk.HORIZONTAL, bg='#1a1a1a', sashwidth=8)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left: Markdown Editor
        editor_frame = tk.Frame(paned, bg='#1e1e1e')
        paned.add(editor_frame, width=600)
        
        tk.Label(editor_frame, text="MARKDOWN", bg='#1e1e1e', fg='#555',
                font=('Arial', 8, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Text widget with scrollbar
        text_frame = tk.Frame(editor_frame, bg='#1e1e1e')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.editor = tk.Text(text_frame, bg='#1e1e1e', fg='#e0e0e0',
                             insertbackground='#fff', font=('Consolas', 11),
                             wrap=tk.WORD, relief='flat', padx=10, pady=10,
                             yscrollcommand=scrollbar.set, undo=True)
        self.editor.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.editor.yview)
        
        # Placeholder
        self.editor.insert('1.0', """# Introduction

Write your blog post here using **Markdown** syntax.

## Features

- Real-time preview
- Export to HTML
- Blog-style formatting

## Code Example

```python
def hello():
    print("Hello, World!")
```

> This is a blockquote for important notes.

Visit [my blog](https://gkfla2020-bit.github.io) for more.
""")
        self.editor.bind('<KeyRelease>', lambda e: self.update_preview())
        
        # Add image button
        tk.Button(btn_frame, text="Add Image", command=self.add_image_dialog,
                 bg='#555', fg='#fff', font=('Arial', 9), relief='flat', padx=15, pady=5,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Right: Preview
        preview_frame = tk.Frame(paned, bg='#fafaf8')
        paned.add(preview_frame, width=600)
        
        tk.Label(preview_frame, text="PREVIEW", bg='#fafaf8', fg='#888',
                font=('Arial', 8, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        
        # HTML preview using Text widget (simplified)
        preview_scroll = tk.Scrollbar(preview_frame)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preview = tk.Text(preview_frame, bg='#fafaf8', fg='#1a1a1a',
                              font=('Georgia', 11), wrap=tk.WORD, relief='flat',
                              padx=20, pady=20, state='disabled',
                              yscrollcommand=preview_scroll.set)
        self.preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        preview_scroll.config(command=self.preview.yview)
        
        # Configure text tags for styling
        self.preview.tag_configure('title', font=('Georgia', 24, 'bold'), spacing3=10)
        self.preview.tag_configure('date', font=('Arial', 9), foreground='#888', spacing3=5)
        self.preview.tag_configure('category', font=('Arial', 8), foreground='#0080c6', spacing3=20)
        self.preview.tag_configure('h1', font=('Georgia', 20, 'bold'), spacing1=20, spacing3=10)
        self.preview.tag_configure('h2', font=('Georgia', 16, 'bold'), spacing1=15, spacing3=8)
        self.preview.tag_configure('h3', font=('Georgia', 13, 'bold'), spacing1=12, spacing3=6)
        self.preview.tag_configure('body', font=('Georgia', 11), spacing3=8)
        self.preview.tag_configure('code', font=('Consolas', 10), background='#f0f0f0')
        self.preview.tag_configure('quote', font=('Georgia', 11, 'italic'), foreground='#555', 
                                  lmargin1=20, lmargin2=20, spacing1=10, spacing3=10)
    
    def update_preview(self):
        """Update the preview pane"""
        content = self.editor.get('1.0', tk.END)
        title = self.title_var.get() or 'Untitled Post'
        date = self.date_var.get()
        category = self.category_var.get() or 'Research'
        
        # Format date
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            date_formatted = date_obj.strftime('%B %d, %Y')
        except:
            date_formatted = date
        
        # Update preview
        self.preview.config(state='normal')
        self.preview.delete('1.0', tk.END)
        
        # Header
        self.preview.insert(tk.END, f"{date_formatted}\n", 'date')
        self.preview.insert(tk.END, f"{title}\n", 'title')
        self.preview.insert(tk.END, f"{category}\n\n", 'category')
        
        # Simple markdown parsing for preview
        lines = content.split('\n')
        in_code_block = False
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                self.preview.insert(tk.END, line + '\n', 'code')
            elif stripped.startswith('# '):
                self.preview.insert(tk.END, stripped[2:] + '\n', 'h1')
            elif stripped.startswith('## '):
                self.preview.insert(tk.END, stripped[3:] + '\n', 'h2')
            elif stripped.startswith('### '):
                self.preview.insert(tk.END, stripped[4:] + '\n', 'h3')
            elif stripped.startswith('> '):
                self.preview.insert(tk.END, stripped[2:] + '\n', 'quote')
            elif stripped.startswith('- ') or stripped.startswith('* '):
                self.preview.insert(tk.END, '  • ' + stripped[2:] + '\n', 'body')
            elif stripped:
                # Handle bold and italic
                text = stripped.replace('**', '').replace('*', '').replace('`', '')
                self.preview.insert(tk.END, text + '\n', 'body')
            else:
                self.preview.insert(tk.END, '\n')
        
        self.preview.config(state='disabled')
    
    def generate_html(self):
        """Generate full HTML with blog template"""
        title = self.title_var.get() or 'Untitled Post'
        date = self.date_var.get()
        category = self.category_var.get() or 'Research'
        content = self.editor.get('1.0', tk.END)
        
        # Format date
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            date_formatted = date_obj.strftime('%B %d, %Y')
        except:
            date_formatted = date
        
        # Convert markdown to HTML
        html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
        
        return f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Ha Rim Jung</title>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;700&family=Space+Mono:wght@400&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Inter', sans-serif; background: #fafaf8; color: #1a1a1a; line-height: 1.7; }}
.container {{ max-width: 800px; margin: 0 auto; padding: 60px 40px; }}
.post-header {{ margin-bottom: 40px; padding-bottom: 30px; border-bottom: 1px solid #e0e0e0; }}
.post-date {{ font-size: .7rem; color: #888; letter-spacing: .15em; text-transform: uppercase; margin-bottom: 15px; }}
.post-title {{ font-family: 'Cormorant Garamond', serif; font-size: 2.5rem; font-weight: 500; line-height: 1.2; margin-bottom: 15px; }}
.post-category {{ display: inline-block; font-size: .65rem; color: #0080c6; letter-spacing: .1em; text-transform: uppercase; padding: 4px 10px; background: rgba(0,128,198,.08); border-radius: 3px; }}
.post-body {{ font-family: 'Georgia', serif; font-size: 17px; line-height: 1.9; }}
.post-body h1 {{ font-family: 'Cormorant Garamond', serif; font-size: 2rem; font-weight: 500; margin: 50px 0 20px; padding-bottom: 10px; border-bottom: 1px solid #e0e0e0; }}
.post-body h2 {{ font-family: 'Cormorant Garamond', serif; font-size: 1.6rem; font-weight: 500; margin: 40px 0 15px; color: #333; }}
.post-body h3 {{ font-size: 1.2rem; font-weight: 600; margin: 30px 0 12px; color: #444; }}
.post-body p {{ margin-bottom: 20px; text-align: justify; }}
.post-body ul, .post-body ol {{ margin: 20px 0 20px 25px; }}
.post-body li {{ margin-bottom: 8px; }}
.post-body blockquote {{ border-left: 3px solid #0080c6; padding: 15px 20px; margin: 25px 0; background: #f8f8f8; font-style: italic; color: #555; }}
.post-body code {{ font-family: 'Space Mono', monospace; background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: .9em; }}
.post-body pre {{ background: #1e1e1e; color: #e0e0e0; padding: 20px; border-radius: 5px; overflow-x: auto; margin: 25px 0; }}
.post-body pre code {{ background: none; padding: 0; color: inherit; }}
.post-body strong {{ font-weight: 600; }}
.post-body a {{ color: #0080c6; text-decoration: none; border-bottom: 1px solid rgba(0,128,198,.3); }}
.post-body a:hover {{ border-bottom-color: #0080c6; }}
.post-body img {{ max-width: 100%; height: auto; margin: 25px 0; border-radius: 5px; }}
.post-body table {{ width: 100%; border-collapse: collapse; margin: 25px 0; font-size: .9rem; }}
.post-body th, .post-body td {{ padding: 12px; border: 1px solid #e0e0e0; text-align: left; }}
.post-body th {{ background: #f5f5f5; font-weight: 600; }}
.back-link {{ display: inline-block; margin-top: 40px; font-size: .85rem; color: #888; text-decoration: none; }}
.back-link:hover {{ color: #0080c6; }}
    </style>
</head>
<body>
<div class="container">
    <div class="post-header">
        <div class="post-date">{date_formatted}</div>
        <h1 class="post-title">{title}</h1>
        <span class="post-category">{category}</span>
    </div>
    <div class="post-body">
{html_content}
    </div>
    <a href="/" class="back-link">← Back to Home</a>
</div>
</body>
</html>'''
    
    def preview_browser(self):
        """Open preview in default browser"""
        html = self.generate_html()
        
        # Create temp file
        if self.temp_html:
            try:
                os.unlink(self.temp_html)
            except:
                pass
        
        fd, self.temp_html = tempfile.mkstemp(suffix='.html')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(html)
        
        webbrowser.open('file://' + self.temp_html)
    
    def save_html(self):
        """Save HTML file"""
        title = self.title_var.get() or 'post'
        filename = title.lower().replace(' ', '-').replace('/', '-')
        
        filepath = filedialog.asksaveasfilename(
            defaultextension='.html',
            filetypes=[('HTML files', '*.html')],
            initialfile=f'{filename}.html'
        )
        
        if filepath:
            html = self.generate_html()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            messagebox.showinfo('Saved', f'Post saved to:\n{filepath}')
    
    def __del__(self):
        """Cleanup temp file"""
        if self.temp_html:
            try:
                os.unlink(self.temp_html)
            except:
                pass
    
    def setup_drag_drop(self):
        """Setup drag and drop for images"""
        self.editor.drop_target_register(DND_FILES)
        self.editor.dnd_bind('<<Drop>>', self.on_drop_image)
    
    def on_drop_image(self, event):
        """Handle dropped image files"""
        files = self.root.tk.splitlist(event.data)
        for filepath in files:
            filepath = filepath.strip('{}')  # Remove curly braces if present
            if filepath.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                self.insert_image(filepath)
    
    def add_image_dialog(self):
        """Open file dialog to add image"""
        filepath = filedialog.askopenfilename(
            filetypes=[
                ('Image files', '*.png *.jpg *.jpeg *.gif *.webp'),
                ('All files', '*.*')
            ]
        )
        if filepath:
            self.insert_image(filepath)
    
    def insert_image(self, filepath):
        """Insert image into editor"""
        # Copy image to post_images folder
        filename = os.path.basename(filepath)
        # Make unique filename
        base, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename
        while os.path.exists(os.path.join(self.images_folder, new_filename)):
            new_filename = f"{base}_{counter}{ext}"
            counter += 1
        
        dest_path = os.path.join(self.images_folder, new_filename)
        shutil.copy2(filepath, dest_path)
        self.images.append(dest_path)
        
        # Insert markdown at cursor position
        markdown_img = f"\n![{base}]({dest_path})\n"
        self.editor.insert(tk.INSERT, markdown_img)
        self.update_preview()

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = BlogEditor(root)
    root.mainloop()
