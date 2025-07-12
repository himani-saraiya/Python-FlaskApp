from flask import Flask, render_template, request, redirect, jsonify
import database
import csv
from io import BytesIO
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

app = Flask(__name__)
database.init_db()

@app.route('/')
@app.route('/')
def index():
    query = request.args.get('q', '').lower()
    students = database.get_all_students()
    students = [{"id": s[0], "name": s[1], "age": s[2]} for s in students]

    if query:
        students = [s for s in students if query in s['name'].lower() or query in str(s['age'])]

    return render_template("index.html", students=students, query=query)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name'].strip()
        age = request.form['age'].strip()
        if not name or not age.isdigit() or int(age) <= 0:
            error = "Please enter valid name and age (greater than 0)."
            return render_template("add_student.html", error=error, student={"name": name, "age": age})
        database.add_student(name, int(age))
        return redirect('/')
    return render_template("add_student.html", student=None)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    student = database.get_student_by_id(id)
    if not student:
        return "Student not found", 404

    if request.method == 'POST':
        name = request.form['name'].strip()
        age = request.form['age'].strip()
        if not name or not age.isdigit() or int(age) <= 0:
            error = "Please enter valid name and age."
            return render_template("add_student.html", error=error, student={"id": id, "name": name, "age": age})
        database.update_student(id, name, int(age))
        return redirect('/')

    return render_template("add_student.html", student={"id": student[0], "name": student[1], "age": student[2]})

@app.route('/delete/<int:id>')
def delete(id):
    database.delete_student(id)
    return redirect('/')

@app.route('/api/students')
def api_students():
    students = database.get_all_students()
    return jsonify([{"id": s[0], "name": s[1], "age": s[2]} for s in students])

@app.route('/export/csv')
def export_csv():
    students = database.get_all_students()

    output = BytesIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Age'])

    for s in students:
        writer.writerow(s)

    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='students.csv')

@app.route('/export/pdf')
def export_pdf():
    students = database.get_all_students()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    data = [['ID', 'Name', 'Age']] + list(students)

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.gray),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))

    doc.build([table])
    buffer.seek(0)
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='students.pdf')




if __name__ == '__main__':
    app.run(debug=True)
