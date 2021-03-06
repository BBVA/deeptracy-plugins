# Copyright 2017 BBVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Blueprint for project endpoints"""

import json

from flask import Blueprint, request
from flask import jsonify

from deeptracy_core.dal.project.model import Project
import deeptracy_core.dal.project.manager as project_manager
from deeptracy_core.dal.database import db
from deeptracy_core.dal.project.project_hooks import ProjectHookType

from .utils import api_error_response

project = Blueprint("project", __name__)


@project.route('/', methods=["POST"])
def post_project():
    """Adds a project to the database

    It receive a Project in the body as a json object and tries to create the project in the database

    Example:
        Body
        {"repo": "http://google.com"}

    :return codes:  201 on success
                    400 on errors
                    409 on a duplicate repo
    """

    data = request.get_json()
    if not data:
        return api_error_response('invalid payload'), 400

    repo = data.get('repo', None)
    if repo is None or repo == '':
        return api_error_response('missing repo'), 400
    else:
        data.pop('repo')  # repo should not be present in data

    name = data.get('name', None)
    if name is None or name == '':
        name = repo.split('/')[-1]
    if data.get('name'):
        data.pop('name')  # name should not be present in data

    email = data.get('email', None)
    if email is not None:
        hook_type = ProjectHookType.EMAIL.name
        hook_data = {"email": email}
    else:
        hook_type = ProjectHookType.NONE.name
        hook_data = {}

    with db.session_scope() as session:
        try:
            project = project_manager.add_project(repo, name, session, hook_type=hook_type, hook_data=hook_data, **data)
            session.commit()
        except Exception as exc:
            session.rollback()
            if 'unique constraint "project_repo_key"' in exc.args[0]:
                return api_error_response('unique constraint project repo {}'.format(repo)), 409
            else:
                return api_error_response(exc.args[0]), 400

        return jsonify(project.to_dict()), 201


@project.route('/<string:project_id>', methods=["GET"])
def get_project(project_id):
    """Show Requested Project

    Queries and returns a project with a passed ID

    Example:

    :return codes:  200 on success
                    404 on errors
    """
    with db.session_scope() as session:
        try:
            project = project_manager.get_project(project_id, session)
        except Exception as exc:
            return api_error_response(exc.args[0]), 404

        return jsonify(project.to_dict()), 200


@project.route('/', methods=["GET"])
def get_projects():
    """List Projects

    Retrieves a list of all projects on database.

    Example:

    :return codes:  200 on success
                    404 on errors
    """
    filter = request.args.get('filter')

    with db.session_scope() as session:
        try:
            if filter:
                if filter == 'count':
                    return jsonify(project_manager.get_projects_count(session)), 200
                else:
                    return api_error_response('Filter not exists'), 400
            else:
                term = request.args.get('term')

                if term:
                    projects = project_manager.get_projects_by_name_term(term, 20, session)
                else:
                    projects = project_manager.get_projects(session)

                project_arr = [project.to_dict() for project in projects]

                return jsonify(project_arr), 200
        except Exception as exc:
            return api_error_response(exc.args[0]), 400


@project.route('/<string:project_id>', methods=["PUT"])
def update_project(project_id):
    """Updates a project on the database

    Update repo url on existing project

    Example:
        Body
        {"repo": "http://google.com"}

    :return codes:  201 on success
                    400 on errors
    """

    data = request.get_json()
    if not data:
        return api_error_response('invalid payload'), 400

    repo = data.get('repo', None)
    if repo is not None or repo == '':
        return api_error_response('can not update repo'), 400

    with db.session_scope() as session:
        try:
            project = project_manager.update_project(project_id, session, **data)
            session.commit()
        except Exception as exc:
            session.rollback()
            return api_error_response(exc.args[0]), 400

        return jsonify(project.to_dict()), 201


@project.route('/<string:project_id>', methods=["DELETE"])
def delete_project(project_id):
    """Remove a project on the database

    Tries to delete the project that you specified in the endpoint on the database

    :return codes:  204 on success (no content)
                    404 on errors (not found)
    """
    with db.session_scope() as session:
        project = session.query(Project).get(project_id)

        try:
            if project:
                project_manager.delete_project(project_id, session)
                session.commit()
            else:
                return api_error_response('project not found'), 404

        except Exception as exc:
            session.rollback()
            return api_error_response(exc.args[0]), 404

        return '', 204


@project.route('/', methods=["DELETE"])
def delete_projects():
    """Remove a project on the database

    Tries to delete the project that you specified in the endpoint on the database

    :return codes:  204 on success (no content)
                    400 on errors
    """
    with db.session_scope() as session:
        try:
            project_manager.delete_projects(session)
            session.commit()
        except Exception as exc:
            session.rollback()
            return api_error_response(exc.args[0]), 400

        return '', 204


@project.route('/<string:project_id>/scans', methods=["GET"])
def get_scans_by_project_id(project_id):
    """Show Requested Scans by Project

    Queries and returns all scans in a project with a passed ID

    Example:

    :return codes:  200 on success
                    404 on errors
    """
    with db.session_scope() as session:
        try:
            scans = [scan.to_dict() for scan in project_manager.get_project(project_id, session).scans]
        except Exception as exc:
            return api_error_response(exc.args[0]), 404

        return jsonify(scans), 200


@project.route('/<string:project_id>/email', methods=["PATCH"])
def patch_project_email(project_id):
    """Update the user email for the Project

    Update the email for the project with project_id

    Example:

    :return codes:  200 on success
                    404 on errors
    """
    with db.session_scope() as session:
        data = request.get_json()
        if not data:
            return api_error_response('invalid payload'), 400

        email = data.get('email', None)
        if email is None or email == '':
            return api_error_response('missing remail'), 400

        try:
            project = project_manager.get_project(project_id, session)
            hook_type = project.hook_type
            if project.hook_data:
                hook_data_dict = json.loads(project.hook_data)
            else:
                hook_data_dict = {}

            if hook_type == ProjectHookType.NONE.name:
                hook_type = ProjectHookType.EMAIL.name
            elif hook_type == ProjectHookType.SLACK.name:
                hook_type = ProjectHookType.SLACK_EMAIL.name

            hook_data_dict['email'] = email
            project_manager.update_project(project_id, session, hook_type=hook_type, hook_data=hook_data_dict)
        except Exception as exc:
            return api_error_response(exc.args[0]), 404

        return jsonify(project.to_dict()), 200
