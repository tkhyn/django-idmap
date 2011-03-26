from idmapper import flush_cache

class FlushIdMapperCache(object):
    def process_response(self, request, response):
        flush_cache()
        return response
