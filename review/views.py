from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from review.models import Review
from review.forms import ReviewForm
from catalog.models import Product
from django.views.decorators.csrf import csrf_exempt
import requests
import json

# Create your views here.
def show_review(request):
    if request.user.is_authenticated:
        if request.user.username.lower() == 'admin':
            review = Review.objects.all()
        else:
            review = Review.objects.filter(user=request.user)
        context = {
            "review": review
        }
        return render(request, "review.html", context)
    else :
        return render(request, "review.html")

@login_required(login_url="authentication:login")
def show_json(request):
    if 'admin' in request.user.username.lower():
        reviews = Review.objects.all()
    else:
        reviews = Review.objects.filter(user=request.user)
    data = [
        {
            'id': str(review.id),
            'date': review.date.strftime("%d %B %Y"),
            'review': review.review,
            'rating': review.rating,
            'product': {
                'name': review.product.name,
                'price': review.product.price,
                'image': review.product.image
            }
        }
        for review in reviews
    ]
    return JsonResponse(data, safe=False)

@login_required(login_url="authentication:login")
def show_json_by_id(request, review_id):
    try:
        if request.user.username.lower() == 'admin':
            review = Review.objects.get(pk=review_id)
        else:
            review = Review.objects.filter(user=request.user).get(pk=review_id)
        data = {
            'id': str(review.id),
            'date': review.date.strftime("%d %B %Y"),
            'review': review.review,
            'rating': review.rating,
            'product': {
                'name': review.product.name,
                'price': review.product.price,
                'image': review.product.image
            }
        }
        return JsonResponse(data)
    except Review.DoesNotExist:
       return JsonResponse({'detail': 'Not found'}, status=404)

@login_required(login_url="authentication:login")
def create_review(request, id):
    product = get_object_or_404(Product, pk=id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if (form.is_valid()):
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return JsonResponse({'status': 'success', 'message': 'Review added!'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    
    form = ReviewForm()
    context = {'form': form}
    return render(request, "review.html", context)

@require_POST
@login_required(login_url="authentication:login")
def edit_review(request, review_id):
    if request.user.username.lower() == 'admin':
        review = get_object_or_404(Review, pk=review_id)
    else:
        review = get_object_or_404(Review, pk=review_id, user=request.user)
    form = ReviewForm(request.POST or None, instance=review)

    if form.is_valid() and request.method == 'POST':
        form.save()
        return JsonResponse({'status': 'success', 'message': 'Review updated!'})
    else:
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    
@require_POST
@login_required(login_url="authentication:login")
def delete_review(request, review_id):
    try:
        if request.user.username.lower() == 'admin':
            review = get_object_or_404(Review, pk=review_id)
        else:
            review = get_object_or_404(Review, pk=review_id, user=request.user)
        review.delete()
        return JsonResponse({'status':'success', 'message':'Review deleted!'})
    except Exception as e:
        return JsonResponse({'status':'error', 'message':str(e)})
    
def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)
    
@csrf_exempt
def show_json_flutter(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Must be logged in"}, status=401)
    
    if 'admin' in request.user.username.lower():
        reviews = Review.objects.all()
    else:
        reviews = Review.objects.filter(user=request.user)
    data = [
        {
            'id': str(review.id),
            'date': review.date.strftime("%d %B %Y"),
            'review': review.review,
            'rating': review.rating,
            'product': {
                'name': review.product.name,
                'price': review.product.price,
                'image': review.product.image
            }
        }
        for review in reviews
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
def create_review_flutter(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product = Product.objects.get(pk=id)
            user = request.user

            review_text = data.get("review", "")
            rating_val = data.get("rating", 0)

            try:
                rating = int(rating_val)
            except ValueError:
                return JsonResponse({"status": "error", "message": "Rating must be a valid number"}, status=400)
            
            if rating < 1 or rating > 5:
                return JsonResponse({"status": "error", "message": "Rating must be between 1 and 5"}, status=400)
            
            new_review = Review(
                user=user,
                product=product,
                review=review_text,
                rating=rating,
            )
            new_review.save()

            return JsonResponse({"status": "success", "message": "Review successfully added"}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Product not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=401)

@csrf_exempt
def edit_review_flutter(request, review_id):
    if request.method == 'POST':
        try:
            if request.user.username.lower() == 'admin':
                review = Review.objects.get(pk=review_id)
            else:
                review = Review.objects.get(pk=review_id, user=request.user)
            
            data = json.loads(request.body)

            review_text = data.get("review", "")
            rating_val = data.get("rating", review.rating)
            
            try:
                rating = int(rating_val)
            except ValueError:
                return JsonResponse({"status": "error", "message": "Rating must be a valid number"}, status=400)

            if rating < 1 or rating > 5:
                return JsonResponse({"status": "error", "message": "Rating must be between 1 and 5"}, status=400)
            
            review.review = review_text
            review.rating = rating
            review.save()
            
            return JsonResponse({"status": "success", "message": "Review successfully updated"}, status=200)
        except Review.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Review not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=401)
    
@csrf_exempt
def delete_review_flutter(request, review_id):
    if request.method == 'POST':
        try:
            if request.user.username.lower() == 'admin':
                review = Review.objects.get(pk=review_id)
            else:
                review = Review.objects.get(pk=review_id, user=request.user)
            
            review.delete()
            return JsonResponse({"status": "success", "message": "Review successfully deleted"}, status=200)
        except Review.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Review not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=401)