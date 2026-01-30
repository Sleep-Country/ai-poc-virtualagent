from fastapi import FastAPI, Request
from flask import jsonify, make_response
from google.cloud import retail_v2
from google.cloud.retail_v2 import SearchRequest, SearchServiceClient
from google.api_core.exceptions import GoogleAPICallError

app = FastAPI()

@app.get("/product_search/")
async def search_http(request: Request):
    """
    An HTTP-triggered Cloud Function that searches products in Vertex AI Search.
    
    Args:
        request (flask.Request): The request object containing query parameters.

    Returns:
        A JSON response with the search results or an error message.
    """
    
    # Get query parameters from the URL (e.g., ?query=mattress&visitorId=1)
    request_args = request.args
    query = "mattress" # request_args.get("query")
    visitor_id = "1" # request_args.get("visitorId")

    if not query or not visitor_id:
        error_msg = {"error": "Both 'query' and 'visitorId' parameters are required."}
        return make_response(jsonify(error_msg), 400)

    # --- Configuration for your specific environment ---
    placement = "projects/sc-retailsearch-dev/locations/global/catalogs/default_catalog/placements/default_search"
    search_client = retail_v2.SearchServiceClient()

    # --- Construct and send the request ---
    search_request = retail_v2.SearchRequest(
        placement=placement,
        query=query,
        visitor_id=visitor_id
    )

    print(f"--- Executing search for query: '{query}', visitor: '{visitor_id}' ---")

    try:
        search_response = search_client.search(request=search_request)
        
        # Manually format the response into a JSON-friendly list of objects
        results_list = []
        for result in search_response.results:
            product = result.product
            price_info = {}
            if product.price_info:
                price_info = {
                    "price": product.price_info.price,
                    "currencyCode": product.price_info.currency_code
                }

            results_list.append({
                "id": result.id,
                "title": product.title,
                "priceInfo": price_info,
                "availability": product.availability.name
            })

        return jsonify(results_list)

    except GoogleAPICallError as e:
        error_msg = {"error": f"An API error occurred: {e.message}"}
        return make_response(jsonify(error_msg), 500)
    except Exception as e:
        error_msg = {"error": f"An unexpected error occurred: {e}"}
        return make_response(jsonify(error_msg), 500)
