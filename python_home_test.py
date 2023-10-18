from flask import Flask, request, jsonify
import pandas

app = Flask(__name__)

file_name = 'datasets/salary_survey.csv'
df = pandas.read_csv(file_name, keep_default_na=False)
raw_data = df.to_dict('records')

def evaluate_filter(item, field, value, operator):
    if operator == 'eq' or operator == '':
        return item[field] == value
    elif operator == 'gte':
        return item[field] >= int(value)
    elif operator == 'lte':
        return item[field] <= int(value)
    else:
        return False

def filter_data(data, filters):
    if filters:
        filtered_data = data.copy()
        for raw_field, value in filters.items():
            if raw_field in ('sort', 'fields'):
                pass
            else:
                field = raw_field.split('[')[0]
                if '[' in raw_field:
                    operator = raw_field.split('[')[1].rstrip(']')
                else:
                    operator = ''
                filtered_data = [item for item in filtered_data if evaluate_filter(item=item, field=field, value=value, operator=operator)]

        return filtered_data
    else:
        return data
def sort_data(data, sort_by):
    if sort_by:
        sorted_data = sorted(data, key=lambda x: x[sort_by])
        return sorted_data
    else:
        return data
def select_fields(data, fields):
    if fields:
        selected_data = [{field: row[field] for field in fields} for row in data]
        return selected_data
    else:
        return data

@app.route('/compensation_data', methods=['GET'])
def get_compensation_data():

    filters = request.args
    for field, value in filters.items():
        if field not in df.columns and field not in ('sort', 'fields'):
            return f'Field "{field}" is not valid request field'

    sort_by = request.args.get('sort')

    fields = request.args.getlist('fields')
    if fields:
        if ',' in fields[0]:
            fields = fields[0].split(',')

    filtered_data = filter_data(raw_data, filters)
    sorted_data = sort_data(filtered_data, sort_by)
    selected_data = select_fields(sorted_data, fields)

    return jsonify(selected_data)

if __name__ == '__main__':
    app.run(debug=True)
