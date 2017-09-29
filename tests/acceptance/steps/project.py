import requests
from sqlalchemy import text
from flask import json
from behave import given, when, then


@given(u'an empty project table in database')
def step_impl(context):
    sql = text('DELETE FROM project')
    context.engine.execute(sql)


@when(u'the user makes a "{method}" request to "{endpoint}" endpoint with {payload}')
def step_impl(context, method, endpoint, payload):
    endpoint = 'http://{}{}'.format(context.SERVER_ADDRESS, endpoint)
    res = requests.request(method, endpoint, json=json.loads(payload))
    context.last_response = res


@then(u'the api response code is {response_code}')
def step_impl(context, response_code):
    assert context.last_response.status_code == int(response_code)


@then(u'the api response payload is {response}')
def step_impl(context, response):
    json_data = json.loads(context.last_response.text)
    json_expected = json.loads(response)

    context.last_project_id = json_data.get('id', None)

    # remove the id from response and expected result
    json_data.pop('id', None)
    json_expected.pop('id', None)
    assert json_data == json_expected


@then(u'{created} projects are in the database')
def step_impl(context, created):
    sql = text('SELECT * FROM project')
    results = context.engine.execute(sql).fetchall()

    assert len(results) == int(created)