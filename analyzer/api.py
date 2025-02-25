# analyzer/api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Product, IngredientAnalysis
from .services import IngredientAnalyzer
from django.conf import settings

class AnalyzeIngredientsAPIView(APIView):
    """API view for analyzing ingredients from text, image or barcode"""
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def post(self, request):
        try:
            # Extract data from request
            name = request.data.get('name', 'Unknown Product')
            category = request.data.get('category')
            
            if not category or category not in ['food', 'beauty']:
                return Response(
                    {"error": "Valid category (food or beauty) is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Handle different input methods
            ingredients_text = None
            barcode = None
            
            # 1. Direct text input
            if 'ingredients_text' in request.data and request.data['ingredients_text']:
                ingredients_text = request.data['ingredients_text']
            
            # 2. Image processing
            elif 'ingredients_image' in request.FILES:
                # You'll need to implement ImageProcessor class for this to work
                from .image_processor import ImageProcessor
                image_processor = ImageProcessor()
                ingredients_text = image_processor.extract_text_from_image(request.FILES['ingredients_image'])
                
                if not ingredients_text:
                    return Response(
                        {"error": "Could not extract text from the image"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # 3. Barcode scanning
            elif 'barcode_image' in request.FILES or 'barcode' in request.data:
                # You'll need to implement BarcodeScanner class for this to work
                from .barcode_scanner import BarcodeScanner
                scanner = BarcodeScanner()
                
                if 'barcode_image' in request.FILES:
                    barcode = scanner.scan_barcode(request.FILES['barcode_image'])
                else:
                    barcode = request.data['barcode']
                
                if not barcode:
                    return Response(
                        {"error": "Could not detect a valid barcode"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
                product_data = scanner.lookup_product(barcode)
                if not product_data:
                    return Response(
                        {"error": f"No product found for barcode {barcode}"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                    
                name = product_data.get('name', name)
                ingredients_text = product_data.get('ingredients_text')
            
            else:
                return Response(
                    {"error": "Please provide ingredients text, image, or barcode"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create product in database
            product = Product.objects.create(
                name=name,
                category=category,
                barcode=barcode,
                ingredients_text=ingredients_text
            )
            
            # Analyze ingredients
            analyzer = IngredientAnalyzer()
            analysis_result = analyzer.analyze(ingredients_text, category)
            
            if not analysis_result:
                return Response(
                    {"error": "Failed to analyze ingredients"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Store analysis in database
            analysis = IngredientAnalysis.objects.create(
                product=product,
                analysis_json=analysis_result,
                overall_rating=analysis_result.get('overall_rating', 5)
            )
            
            # Return result
            return Response({
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "barcode": product.barcode,
                    "ingredients_text": product.ingredients_text
                },
                "analysis": analysis_result
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductHistoryAPIView(APIView):
    """API view for retrieving product history"""
    
    def get(self, request):
        products = Product.objects.all().order_by('-created_at')
        result = []
        
        for product in products:
            try:
                analysis = IngredientAnalysis.objects.get(product=product)
                result.append({
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "barcode": product.barcode,
                    "overall_rating": analysis.overall_rating,
                    "analyzed_at": analysis.analyzed_at
                })
            except IngredientAnalysis.DoesNotExist:
                continue
                
        return Response(result, status=status.HTTP_200_OK)


class ProductDetailAPIView(APIView):
    """API view for retrieving specific product details"""
    
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            analysis = IngredientAnalysis.objects.get(product=product)
            
            return Response({
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "barcode": product.barcode,
                    "ingredients_text": product.ingredients_text,
                    "created_at": product.created_at
                },
                "analysis": analysis.analysis_json
            }, status=status.HTTP_200_OK)
            
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except IngredientAnalysis.DoesNotExist:
            return Response(
                {"error": "Analysis not found for this product"}, 
                status=status.HTTP_404_NOT_FOUND
            )