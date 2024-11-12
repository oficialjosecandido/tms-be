import json
from rest.serializers import *
from rest_framework.decorators import api_view
from rest.models import *
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination


@api_view(['GET'])
def all_listings(request):
    try:
        listings = Listing.objects.order_by('-created_at')
        serializer = ListingSerializer(listings, many=True)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Listings not found"}, status=404)

@api_view(['GET'])
def listing_id(request, id):
    try:
        listing = Listing.objects.get(id=id)
        # Check if the close_date has passed
        if listing.close_date and listing.close_date < timezone.now():
            # Update the status to 'Closed' if the close_date has passed
            listing.status = 'Closed'
            listing.save()

        serializer = ListingSerializer(listing)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Listing not found"}, status=404)

@api_view(['GET'])
def listing_detail(request, slug):
    try:
        listing = Listing.objects.get(slug=slug)
        # Check if the close_date has passed
        if listing.close_date and listing.close_date < timezone.now():
            # Update the status to 'Closed' if the close_date has passed
            listing.status = 'Closed'
            listing.save()

        serializer = ListingSerializer(listing)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Listing not found"}, status=404)
    

@api_view(['GET'])
def listing_images(request, slug):
    try:
        listing = get_object_or_404(Listing, slug=slug)
        images = ListingImage.objects.filter(listing=listing)
        serializer = ListingImageSerializer(images, many=True)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Listing not found"}, status=404)

@csrf_exempt
@api_view(['POST'])
def create_listing(request):
    if request.method == 'POST':
        try:
            # Extract text data from the request
            title = request.POST.get('title')
            category = request.POST.get('category')
            brand = request.POST.get('brand')
            buynow_price = request.POST.get('buynow_price')
            starting_price = request.POST.get('starting_price')
            condition = request.POST.get('condition')
            excerpt = request.POST.get('excerpt')
            description = request.POST.get('description')
            duration = request.POST.get('duration')
            promoted = request.POST.get('promoted') == 'true'
            location_address1 = request.POST.get('location_address1')
            location_address2 = request.POST.get('location_address2')
            location_city = request.POST.get('location_city')
            location_zipcode = request.POST.get('location_zipcode')
            customer_id = request.POST.get('customer_id')
            customer_name = request.POST.get('customer_name')
            customer_email = request.POST.get('customer_email')
            print('POST request', request.POST)

            # Validate required fields
            if not title or not category:
                return JsonResponse({'error': 'Missing required fields: title, category'}, status=400)
            
            # Validate duration field
            if duration not in ['3', '7', '30']:
                duration = 30
                #return JsonResponse({'error': 'Invalid duration. Must be 3, 7, or 30 days.'}, status=400)

            duration_days = int(duration)
            close_date = timezone.now() + timedelta(days=duration_days)

            # Fetch customer based on ID
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                customer = Customer.objects.create(
                    email = customer_email,
                    display_name = customer_name
                )
                # return JsonResponse({'error': 'Customer not found'}, status=404)
            
            # Extract and save image files
            image_files = request.FILES.getlist('files')  # Assuming 'files' is the key for images in form-data
            

            # Create a new Listing object
            listing = Listing.objects.create(
                title=title,
                category=category,
                brand=brand,
                buynow_price=buynow_price,
                starting_price=starting_price,
                condition=condition,
                excerpt=excerpt,
                description=description,
                duration=duration,
                promoted=promoted,
                location_address1=location_address1,
                location_address2=location_address2,
                location_city=location_city,
                location_zipcode=location_zipcode,
                image = image_files[0],
                customer=customer,
                close_date=close_date 
            )

            #save image files
            if image_files:
                for image_file in image_files:
                    ListingImage.objects.create(listing=listing, image=image_file)
            else:
                return JsonResponse({'error': 'No images provided'}, status=400)

            

            # Send email notification to the user
            subject = 'Listing Created and Pending Approval'
            message = render_to_string('emails/N0003_create_listing_success.html', {
                'customer_name': listing.customer.display_name,
                'listing_link': 'https://trademyspin.web.app/listing/' + str(listing.slug)
            })
            plain_message = strip_tags(message)
            from_email = settings.EMAIL_HOST_USER
            to_email = [customer.email]
            send_mail(subject, plain_message, from_email, to_email, html_message=message)


            # Return a JSON response including the created listing
            return JsonResponse({'message': 'Listing created successfully', 'listing': {
                'id': listing.id,
                'customer': {
                    'name': customer.display_name,
                    'email': customer.email,
                    'phone_number': customer.phone_number
                },
                'status': listing.status,
                'created_at': listing.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }}, status=201)

        except Exception as e:
            # Log the error for debugging
            print(e)
            # Return an error response if something goes wrong
            return JsonResponse({'error': str(e)}, status=500)
    else:
        # Return a method not allowed response for non-POST requests
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@api_view(['GET'])
def my_listings(request, identifier):

    print(2222, identifier)
    customer = Customer.objects.get(email=identifier)

    try:
        listings = Listing.objects.filter(customer=customer).order_by('-created_at')
        for listing in listings:
            if listing.status == 'Pending Confirmation':
                listing.status = 'Active'
                print(listing)
                listing.save()
        serializer = ListingSerializer(listings, many=True)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Listings not found"}, status=404)
    


@api_view(['GET'])
def listings_category(request, categ):
    try:
        sort_option = request.GET.get('sort', 'close_date')
        
        sort_fields = {
            'added': '-created_at',  
            'closing': 'close_date',  
            'price': 'starting_price'  
        }
        
        order_by_field = sort_fields.get(sort_option, 'close_date')
        listings = Listing.objects.filter(category=categ, status='Active').order_by(order_by_field)
        # Pagination
        paginator = ListingPagination()
        result_page = paginator.paginate_queryset(listings, request)
        serializer = ListingSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Listing.DoesNotExist:
        return Response({"error": "Listings not found"}, status=404)

    

@api_view(['GET'])
def search_listings(request, search):
    try:
        sort_option = request.GET.get('sort', 'close_date')
        
        sort_fields = {
            'added': '-created_at',  
            'closing': 'close_date',  
            'price': 'starting_price'  
        }
        
        order_by_field = sort_fields.get(sort_option, 'close_date')
        
        # Filter listings based on search term (title or excerpt)
        listings = Listing.objects.filter(
            Q(title__icontains=search) | Q(excerpt__icontains=search)
        ).filter(status='Active').order_by(order_by_field)
        
        # Pagination logic
        paginator = ListingPagination()
        paginated_listings = paginator.paginate_queryset(listings, request)
        
        # Serialize the paginated listings
        serializer = ListingSerializer(paginated_listings, many=True)
        
        # Return paginated response
        return paginator.get_paginated_response(serializer.data)
    
    except Listing.DoesNotExist:
        return Response({"error": "Listings not found"}, status=404)


class ListingPagination(PageNumberPagination):
    page_size = 12  # Default page size
    page_size_query_param = 'page_size'  # Allow client to change page size
    max_page_size = 100  # Max limit