# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from apps.home import blueprint
from flask import render_template, request, jsonify
from sqlalchemy.ext.serializer import loads, dumps
from flask_login import login_required
from jinja2 import TemplateNotFound
from sqlalchemy.orm import sessionmaker
from .spog.database import postgresbind, kingsCollegeLondonRCSApplications
import json


def dict_helper(objlist):
    result2 = [item.obj_to_dict() for item in objlist]
    return result2


@blueprint.route("/index")
@login_required
def index():
    Session = sessionmaker(bind=postgresbind())
    with Session() as session:
        result = session.query(kingsCollegeLondonRCSApplications).all()
    return render_template("home/index.html", segment="index", applications=result)


@blueprint.route("/overview")
@login_required
def overview():
    Session = sessionmaker(bind=postgresbind())
    with Session() as session:
        result = session.query(kingsCollegeLondonRCSApplications).all()
    return render_template("home/overview.html", segment="overview", data=result)


@blueprint.route("/applications", methods=["GET"])
@login_required
def resarchCloudApplications():
    Session = sessionmaker(bind=postgresbind())
    with Session() as session:
        result = session.query(kingsCollegeLondonRCSApplications.name).all()
        data = json.dumps([dict(r) for r in result])
        apps = json.loads(data)
        return jsonify(apps)


@blueprint.route("/applicationsummary", methods=["GET"])
@login_required
def applicationSummary():
    Session = sessionmaker(bind=postgresbind())
    with Session() as session:
        result = session.query(
            kingsCollegeLondonRCSApplications.name,
            kingsCollegeLondonRCSApplications.contact,
            kingsCollegeLondonRCSApplications.cloudabilityviewid,
            kingsCollegeLondonRCSApplications.uuid,
            kingsCollegeLondonRCSApplications.platform,
        ).all()
        data = json.dumps([dict(r) for r in result])
        apps = json.loads(data)
        return jsonify(apps)


@blueprint.route("/<template>")
@login_required
def route_template(template):

    try:

        if not template.endswith(".html"):
            template += ".html"

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template("home/page-404.html"), 404

    except:
        return render_template("home/page-500.html"), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split("/")[-1]

        if segment == "":
            segment = "index"

        return segment

    except:
        return None
