from flask import Blueprint

blueprint=Blueprint("Map", __name__)

@blueprint.route("/map")
def intersect():
    return "Map",200