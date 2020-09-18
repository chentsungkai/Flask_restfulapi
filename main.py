from flask import Flask  , jsonify , request
from flask_restful import Api,Resource , reqparse , abort , marshal_with , fields
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///database.db'
db = SQLAlchemy(app)

class VideoModel(db.Model):
    id  = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable = False )
    view = db.Column(db.Integer,nullable = False)
    likes = db.Column(db.Integer,nullable = False)


    def __repr__(self):
        return "video (name={name},view={view},likes={likes})"

resource_filed = {
    'id':fields.Integer,
    'name':fields.String,
    'view':fields.Integer,
    'likes':fields.Integer
}



video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name",type=str,help="Name of video not found",required=True)
video_put_args.add_argument("view",type=int,help="View of video not found",required=True)
video_put_args.add_argument("likes",type=int,help="Likes of video not found",required=True)

video_update_args = reqparse.RequestParser()
video_update_args.add_argument("name",type=str,help="Name of video not found")
video_update_args.add_argument("view",type=int,help="View of video not found")
video_update_args.add_argument("likes",type=int,help="Likes of video not found")

def video_not_exist(video_id):
    args = video_update_args.parse_args()
    result = VideoModel.query.filter_by(id=video_id)
    if video_id not in result:
        abort(409,message="video not found , can't delete air")

class video(Resource):
    @marshal_with(resource_filed)
    def get(self,video_id):
        result = VideoModel.query.filter_by(id=video_id).first()
        return result

    @marshal_with(resource_filed)
    def put(self,video_id):
        args = video_put_args.parse_args()
        result = VideoModel.query.filter_by(id=video_id).first()
        if result:
            abort(409,message="video id taken")

        video = VideoModel(id=video_id,name=args['name'],view=args['view'],likes=args['likes'])
        db.session.add(video)
        db.session.commit()
        return video,201

    @marshal_with(resource_filed)
    def patch(self,video_id):
        args = video_update_args.parse_args()
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(409,message="video not exist,can't update")

        if args['name']:
            result.name = args['name']
        if args['view']:
            result.view = args['view']
        if args['likes']:
            result.likes= args['likes']

        db.session.commit()

        return result

    def delete(self,video_id):
        video_not_exist(video_id)
        return print("nigger you good")

api.add_resource(video, "/video/<int:video_id>")


if __name__ == "__main__":
    app.run(debug=True)