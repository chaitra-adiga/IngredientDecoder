from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Product, IngredientAnalysis
from .serializers import ProductSerializer, AnalysisSerializer
from .services import IngredientAnalyzer
from .image_processor import ImageProcessor
from .barcode_scanner import BarcodeScanner
from django.shortcuts import render, get_object_or_404, redirect

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def analyze_ingredients(request):
    """Analyze ingredients from text, image, or barcode"""
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
            image_processor = ImageProcessor()
            ingredients_text = image_processor.extract_text_from_image(request.FILES['ingredients_image'])
            
            if not ingredients_text:
                return Response(
                    {"error": "Could not extract text from the image"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 3. Barcode scanning
        elif 'barcode_image' in request.FILES:
            scanner = BarcodeScanner()
            barcode = scanner.scan_barcode(request.FILES['barcode_image'])
            
            if not barcode:
                return Response(
                    {"error": "Could not detect a barcode in the image"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            product_data = scanner.lookup_product(barcode)
            if not product_data:
                return Response(
                    {"error": f"No product found for barcode {barcode}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
            name = product_data.get('name')
            ingredients_text = product_data.get('ingredients_text')
        
        # 4. Direct barcode input
        elif 'barcode' in request.data and request.data['barcode']:
            barcode = request.data['barcode']
            scanner = BarcodeScanner()
            product_data = scanner.lookup_product(barcode)
            
            if not product_data:
                return Response(
                    {"error": f"No product found for barcode {barcode}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
            name = product_data.get('name')
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
            "product": ProductSerializer(product).data,
            "analysis": analysis_result
        })
        
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def product_history(request):
    """Get list of previously analyzed products"""
    products = Product.objects.all().order_by('-created_at')
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product_detail(request, product_id):
    """Get detailed analysis for a specific product"""
    try:
        product = Product.objects.get(id=product_id)
        analysis = IngredientAnalysis.objects.get(product=product)
        
        return Response({
            "product": ProductSerializer(product).data,
            "analysis": analysis.analysis_json
        })
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

# Frontend Views
def home(request):
    """Home page with input forms"""
    return render(request, 'analyzer/home.html')

def history(request):
    """Show history of analyzed products"""
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'analyzer/history.html', {'products': products})

def product_details(request, product_id):
    """Show detailed analysis for a product"""
    product = get_object_or_404(Product, id=product_id)
    analysis = get_object_or_404(IngredientAnalysis, product=product)
    return render(request, 'analyzer/product_details.html', {
        'product': product,
        'analysis': analysis,
    })