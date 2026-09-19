from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

notes_file = 'notes.json'


def load_notes():
    if os.path.exists(notes_file):
        with open(notes_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_notes(notes):
    with open(notes_file, 'w') as f:
        json.dump(notes, f, indent=2)


@app.route('/')
def index():
    notes = load_notes()
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Note Tracker Web</title>
    </head>
    <body>
      <h1>Note Tracker</h1>
      <form id="noteForm">
        <input type="text" id="noteInput" placeholder="Enter note here" required>
        <button type="submit">Add Note</button>
      </form>
      <ul id="notesList">
        {% for idx, note in enumerate(notes) %}
          <li>{{ idx+1 }}. {{ note }} <button onclick="deleteNote({{ idx }})">Delete</button></li>
        {% endfor %}
      </ul>
      <script>
        const form = document.getElementById('noteForm');
        const noteInput = document.getElementById('noteInput');
        const notesList = document.getElementById('notesList');

        form.onsubmit = async (e) => {
          e.preventDefault();
          const note = noteInput.value.trim();
          if (!note) return;

          const resp = await fetch('/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ note })
          });
          if (resp.ok) {
            noteInput.value = '';
            loadNotes();
          } else {
            alert('Failed to add note');
          }
        };

        async function loadNotes() {
          const resp = await fetch('/list');
          if (!resp.ok) return;
          const data = await resp.json();
          notesList.innerHTML = '';
          data.notes.forEach((note, idx) => {
            const li = document.createElement('li');
            li.textContent = `${idx + 1}. ${note} `;
            const delBtn = document.createElement('button');
            delBtn.textContent = 'Delete';
            delBtn.onclick = () => deleteNote(idx);
            li.appendChild(delBtn);
            notesList.appendChild(li);
          });
        }

        async function deleteNote(idx) {
          const resp = await fetch('/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ index: idx })
          });
          if (resp.ok) {
            loadNotes();
          } else {
            alert('Failed to delete note');
          }
        }

        // Initial load
        loadNotes();
      </script>
    </body>
    </html>
    ''', notes=load_notes())


@app.route('/add', methods=['POST'])
def add_note():
    data = request.get_json()
    note = data.get('note', '').strip()
    if not note:
        return jsonify({'error': 'Empty note'}), 400

    notes = load_notes()
    notes.append(note)
    save_notes(notes)
    return jsonify({'success': True})


@app.route('/list')
def list_notes():
    notes = load_notes()
    return jsonify({'notes': notes})


@app.route('/delete', methods=['POST'])
def delete_note():
    data = request.get_json()
    idx = data.get('index')
    notes = load_notes()
    if idx is None or idx < 0 or idx >= len(notes):
        return jsonify({'error': 'Invalid index'}), 400
    notes.pop(idx)
    save_notes(notes)
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # Expose on port 8080 for web access
