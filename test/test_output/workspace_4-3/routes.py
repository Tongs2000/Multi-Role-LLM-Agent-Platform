from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Article, User
from auth import login, register
import bleach
import markdown

def init_routes(app):
    @app.route('/api/register', methods=['POST'])
    def handle_register():
        data = request.get_json()
        return register(data['username'], data['email'], data['password'])

    @app.route('/api/login', methods=['POST'])
    def handle_login():
        data = request.get_json()
        return login(data['username'], data['password'])

    @app.route('/api/articles', methods=['GET'])
    def get_articles():
        articles = Article.query.filter_by(published=True).all()
        return jsonify([article.to_dict() for article in articles])

    @app.route('/api/articles/<slug>', methods=['GET'])
    def get_article(slug):
        article = Article.query.filter_by(slug=slug, published=True).first()
        if not article:
            return {'error': 'Article not found'}, 404
        return jsonify(article.to_dict())

    @app.route('/api/admin/articles', methods=['GET'])
    @jwt_required()
    def get_admin_articles():
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user.is_admin:
            return {'error': 'Unauthorized'}, 403
        
        articles = Article.query.all()
        return jsonify([article.to_dict() for article in articles])

    @app.route('/api/admin/articles', methods=['POST'])
    @jwt_required()
    def create_article():
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Sanitize HTML and convert markdown
        content = bleach.clean(data['content'])
        if data.get('is_markdown', False):
            content = markdown.markdown(content)
        
        article = Article(
            title=data['title'],
            slug=data['slug'],
            content=content,
            excerpt=data.get('excerpt', ''),
            published=data.get('published', False),
            user_id=user_id,
            meta_title=data.get('meta_title', data['title']),
            meta_description=data.get('meta_description', data.get('excerpt', ''))
        )
        db.session.add(article)
        db.session.commit()
        return jsonify(article.to_dict()), 201

    @app.route('/api/admin/articles/<int:id>', methods=['PUT'])
    @jwt_required()
    def update_article(id):
        user_id = get_jwt_identity()
        article = Article.query.get_or_404(id)
        
        if article.user_id != user_id:
            return {'error': 'Unauthorized'}, 403
        
        data = request.get_json()
        article.title = data.get('title', article.title)
        article.slug = data.get('slug', article.slug)
        article.content = bleach.clean(data.get('content', article.content))
        article.excerpt = data.get('excerpt', article.excerpt)
        article.published = data.get('published', article.published)
        article.meta_title = data.get('meta_title', article.meta_title)
        article.meta_description = data.get('meta_description', article.meta_description)
        
        db.session.commit()
        return jsonify(article.to_dict())

    @app.route('/api/admin/articles/<int:id>', methods=['DELETE'])
    @jwt_required()
    def delete_article(id):
        user_id = get_jwt_identity()
        article = Article.query.get_or_404(id)
        
        if article.user_id != user_id:
            return {'error': 'Unauthorized'}, 403
        
        db.session.delete(article)
        db.session.commit()
        return {'message': 'Article deleted'}, 200