"""
Middleware для отключения кеширования в Telegram Web App.
"""


class NoCacheMiddleware:
    """
    Middleware для добавления заголовков, отключающих кеширование.
    Особенно важно для Telegram Web App, который агрессивно кеширует контент.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Применяем заголовки для всех запросов webapp и API
        is_webapp_request = (
            '/api/webapp/' in request.path or
            request.path.startswith('/api/webapp') or
            'webapp' in request.path.lower()
        )
        
        # Применяем заголовки к HTML страницам, JSON ответам и webapp запросам
        if hasattr(response, 'get'):
            content_type = response.get('Content-Type', '')
            is_html = content_type.startswith('text/html')
            is_json = content_type.startswith('application/json')
            is_javascript = content_type.startswith('application/javascript') or content_type.startswith('text/javascript')
            is_css = content_type.startswith('text/css')
            
            if is_webapp_request or is_html or is_json or (is_javascript and is_webapp_request) or (is_css and is_webapp_request):
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
                response['X-Accel-Expires'] = '0'  # Для nginx
                # Дополнительные заголовки для надежности
                if 'ETag' in response:
                    del response['ETag']
                if 'Last-Modified' in response:
                    del response['Last-Modified']
        
        return response

