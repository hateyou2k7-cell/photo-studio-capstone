from flask import request


def paginate(query, schema, default_page_size=20, max_page_size=100):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', default_page_size, type=int)
    if per_page > max_page_size:
        per_page = max_page_size
    if per_page < 1:
        per_page = default_page_size
    if page < 1:
        page = 1

    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return {
        'items': schema.dump(items, many=True),
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page,
    }


def paginate_list(items, schema, default_page_size=20):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', default_page_size, type=int)
    if per_page > 100:
        per_page = 100
    if per_page < 1:
        per_page = default_page_size
    if page < 1:
        page = 1

    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    page_items = items[start:end]
    return {
        'items': schema.dump(page_items, many=True),
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page,
    }
