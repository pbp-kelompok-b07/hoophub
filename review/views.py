from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from review.models import Review
from review.forms import ReviewForm
from catalog.models import Product

# Create your views here.
def show_review(request):
    if request.user.is_authenticated:
        if 'admin' in request.user.username.lower():
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
        if 'admin' in request.user.username.lower():
            review = Review.objects.get(pk=review_id)
        else:
            review = Review.objects.filter(user=request.user).get(pk=review_id)
        data = {
            'id': str(review.id),
            'date': review.date.strftime("%d %B %Y, %H:%M"),
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
    if 'admin' in request.user.username.lower():
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
        if 'admin' in request.user.username.lower():
            review = get_object_or_404(Review, pk=review_id)
        else:
            review = get_object_or_404(Review, pk=review_id, user=request.user)
        review.delete()
        return JsonResponse({'status':'success', 'message':'Review deleted!'})
    except Exception as e:
        return JsonResponse({'status':'error', 'message':str(e)})
