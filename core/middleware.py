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
        
        # Применяем заголовки только к HTML страницам и API
        if (hasattr(response, 'get') and 
            (response.get('Content-Type', '').startswith('text/html') or
             response.get('Content-Type', '').startswith('application/json') or
             '/api/webapp/' in request.path)):
            
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response

