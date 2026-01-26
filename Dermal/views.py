from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
import base64
import re
import httpx
import json
from .fastapi import fast_api
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, login, logout
from .models import *
# from .AI_detection import predict_skin_with_explanation
# from .gardio import gardio
import traceback
import os
import requests
import markdown2
import bleach
from django.views.decorators.http import require_http_methods, require_POST
from django.core.files.storage import default_storage
from django.urls import reverse
from gradio_client import Client
from google import genai
from .translate_result import translate
# Create your views here.
# def user

@require_http_methods(["GET", "HEAD"])
def health(request):
    return JsonResponse({"status": "ok"})

@csrf_exempt
@login_required
def upload_file(request):
    # client = Client("https://codedr-skin-detection.hf.space", timeout=300)
    if request.method == "POST":
        try:
            uploaded_file = request.FILES.get("image")
            if not uploaded_file:
                return JsonResponse({"error": "Không có dữ liệu ảnh"}, status=400)

            img_bytes = uploaded_file.read()
            file_name = uploaded_file.name

            image_file = ContentFile(img_bytes, name=file_name)

            # Gọi model dự đoán với giải thích heatmap
            # results, heatmap_base64 = predict_skin_with_explanation(img_bytes)
            # output = client.predict(img_bytes, api_name="/predict_with_gradcam")
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            output = fast_api(img_b64)

            heat_img_bytes = base64.b64decode(output['heatmap_base64'])
            heatmap_file = ContentFile(
                heat_img_bytes, name="heatmap_"+file_name)

            # Lưu vào DB
            skin_img = Dermal_image.objects.create(
                image=image_file,
                result=output['results'],
                heatmap=heatmap_file,
                user=Profile.objects.get(user=request.user),
                #result_en = translate_result(output['results'])
            )
            """
            skin_img.image.save("skin_image.jpg", image_file)
            skin_img.heatmap.save("heatmap_"+file_name, heatmap_file)
            skin_img.save()
            """

            return redirect('result', image_id=skin_img.id)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Chỉ hỗ trợ POST"}, status=405)


@csrf_exempt
@login_required
def upload_image(request):
    # client = Client("https://codedr-skin-detection.hf.space")
    if request.method == "POST":
        try:
            # Check for file upload (from modal)
            uploaded_file = request.FILES.get("image")
            if uploaded_file:
                # Read file content into bytes
                img_bytes = uploaded_file.read()
                file_name = uploaded_file.name
            else:
                # Check for base64 data (from camera capture)
                image_data = request.POST.get("image")
                if not image_data:
                    return JsonResponse({"error": "Không có dữ liệu ảnh"}, status=400)

                # Bỏ header base64
                img_str = re.sub("^data:image/.+;base64,", "", image_data)
                img_bytes = base64.b64decode(img_str)
                file_name = "skin_capture.jpg"

            # Lưu ảnh vào ImageField
            image_file = ContentFile(img_bytes, name=file_name)

            # Gọi model dự đoán với giải thích heatmap
            # results, heatmap_base64 = predict_skin_with_explanation(img_bytes)
            image_b64 = base64.b64encode(img_bytes).decode("utf-8")
            # output = client.predict(image_b64, api_name="/predict_with_gradcam")
            output = fast_api(image_b64)

            heat_img_bytes = base64.b64decode(output['heatmap_base64'])
            heatmap_file = ContentFile(
                heat_img_bytes, name="heatmap_"+file_name)

            # Lưu vào DB
            skin_img = Dermal_image.objects.create(
                image=image_file,
                result=output['results'],
                heatmap=heatmap_file,
                user=Profile.objects.get(user=request.user),
                #result_en = translate_result(output['results'])
            )
            """
            skin_img.image.save("skin_image.jpg", image_file)
            skin_img.heatmap.save("heatmap_"+file_name, heatmap_file)
            skin_img.save()
            """

            return redirect('result', image_id=skin_img.id)

            """
            return JsonResponse({
                "message": "Lưu thành công",
                "id": skin_img.id,
                "prediction": skin_img.prediction,
                "created_at": skin_img.created_at,
                "image_url": skin_img.image.url,
                "heatmap": heatmap_base64
            })
            """

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Chỉ hỗ trợ POST"}, status=405)


@csrf_exempt
@login_required
def chatbot_api(request):
    """Simple endpoint for chatbot.html to POST a message and receive a reply.

    Expects JSON: { "message": "..." }
    Returns JSON: { "reply": "..." }
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Chỉ hỗ trợ POST"}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
        message = body.get('message', '').strip()
        if not message:
            return JsonResponse({"error": "Thiếu trường 'message'"}, status=400)

        # Call helper to get a reply from Gemini (or fallback)
        reply = call_gemini(message, user=request.user)

        # Truncate very long replies to a reasonable size (avoid huge payloads)
        max_len = 16000
        if isinstance(reply, str) and len(reply) > max_len:
            reply = reply[:max_len] + "\n\n...[truncated]"

        # Convert Markdown (if any) to HTML and sanitize it for safe rendering in client
        try:
            raw_html = markdown2.markdown(
                reply) if isinstance(reply, str) else ''
            allowed_tags = [
                'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'p', 'pre',
                'strong', 'ul', 'br', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
            ]
            allowed_attrs = {
                'a': ['href', 'title', 'rel', 'target']
            }
            clean_html = bleach.clean(raw_html, tags=allowed_tags, attributes=allowed_attrs, protocols=[
                                      'http', 'https', 'mailto'])
            clean_html = bleach.linkify(clean_html)
        except Exception:
            clean_html = ''

        return JsonResponse({"reply": reply, "reply_html": clean_html})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def call_gemini(prompt, user=None):
    """Call Gemini-like API using environment variables.

    This helper tries to call an external Gemini endpoint configured via:
      - GEMINI_API_URL (full URL)
      - GEMINI_API_KEY (auth header: Bearer)

    If those are not set, return a safe canned response.
    """
    api_url = os.getenv('GEMINI_API_URL')
    api_key = os.getenv('GEMINI_API_KEY')

    print(api_key)

    # Basic canned fallback reply (useful for local dev)
    fallback = (
        "Xin chào! Mình hiện đang chạy ở môi trường phát triển nên chưa kết nối được với dịch vụ Gemini.")

    if not api_url or not api_key:
        # Return a simple echo-like placeholder for now
        return f"[DEV REPLY] Mình đã nhận: {prompt[:400]}"

    try:
        # Prefer the official Google Generative AI Python client when available.
        """
        try:
            from google import genai  # type: ignore
        except Exception:
            genai = None

        print(genai)
        """

        model = os.getenv('GEMINI_MODEL') or os.getenv(
            'GEMINI_DEFAULT_MODEL') or 'gemini-2.5-flash-lite'
        print(model)

        if api_key:
            # configure client if possible
            try:
                client = genai.Client(api_key=api_key)
                print(1)
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite", contents=prompt)
                print(response.text)
                return response.text if response and hasattr(response, 'text') else fallback

            except Exception as e:
                # If the SDK call fails, we'll try an HTTP fallback below
                print(e)
                traceback.print_exc()

        # If we have an api_url, try a simple HTTP POST (backward compatible)
        """
        if api_url:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            }
            payload = {
                'prompt': prompt,
                'max_tokens': 512,
                'model': model,
            }
            resp = requests.post(api_url, headers=headers,
                                 json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            # Attempt to pull the reply from common shapes
            if isinstance(data, dict):
                for key in ('reply', 'text', 'output', 'message'):
                    if key in data and isinstance(data[key], str):
                        return data[key]
                if 'choices' in data and isinstance(data['choices'], list) and data['choices']:
                    first = data['choices'][0]
                    if isinstance(first, dict):
                        return first.get('text') or first.get('message') or json.dumps(first)

            return json.dumps(data)
        """

    except Exception as e:
        # final fallback (dev-friendly)
        print(e)
        traceback.print_exc()
        return fallback


from django.contrib import messages
from django.db import IntegrityError

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username') or request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, _("Tên đăng nhập hoặc mật khẩu không chính xác."))
            return render(request, 'login.html', {'data': request.POST})
    return render(request, 'login.html')


def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        avatar = request.FILES.get('avatar')
        birth_date = request.POST.get('birth_date')
        
        try:
            if User.objects.filter(username=username).exists():
                messages.error(request, _("Tên đăng nhập đã tồn tại."))
                return render(request, 'signup.html', {'data': request.POST})
            
            if User.objects.filter(email=email).exists():
                messages.error(request, _("Email đã được sử dụng."))
                return render(request, 'signup.html', {'data': request.POST})

            user = User.objects.create_user(
                username=username, email=email, password=password)
            
            # Use get_or_create because the signal might have already created it
            profile, created = Profile.objects.get_or_create(user=user)
            if birth_date:
                profile.birth_date = birth_date
            if avatar:
                profile.avatar = avatar
            profile.save()
            
            login(request, user)
            return redirect('home')
        except Exception as e:
            messages.error(request, _("Đã xảy ra lỗi trong quá trình đăng ký: ") + str(e))
            return render(request, 'signup.html', {'data': request.POST})
            
    return render(request, 'signup.html')


@login_required
def home_view(request):
    return render(request, 'home.html')


@login_required
def result_view(request, image_id):
    try:
        skin_image = Dermal_image.objects.get(
            id=image_id, user__user=request.user)
        return render(request, 'result.html', {'skin_image': skin_image})
    except Dermal_image.DoesNotExist:
        return JsonResponse({"error": "Ảnh không tồn tại hoặc không có quyền truy cập"}, status=404)


@login_required
def chatbot_view(request):
    return render(request, 'chatbot.html')


@login_required
def community_view(request):
    # Render community feed (latest posts first)
    profile = Profile.objects.get(user=request.user)
    posts = Post.objects.select_related(
        'author__user').order_by('-created_at')[:50]
    # Normalize posts for template: provide image_url if Post has an image field in future
    # Defensive: strip any accidental Django template tags that might be stored in post content

    def strip_template_tags(html_text):
        if not html_text:
            return html_text
        # Remove common Django template tokens like {% ... %} and {{ ... }}
        cleaned = re.sub(r"\{\%[\s\S]*?\%\}", '', html_text)
        cleaned = re.sub(r"\{\{[\s\S]*?\}\}", '', cleaned)
        return cleaned

    cleaned_posts = []
    for p in posts:
        p_safe = p
        try:
            p_safe.content = strip_template_tags(p_safe.content)
        except Exception:
            p_safe.content = ''
        # attach image_url if set earlier in code paths
        if not hasattr(p_safe, 'image_url') and getattr(p_safe, 'image', None):
            try:
                p_safe.image_url = p_safe.image.url
            except Exception:
                p_safe.image_url = None
        cleaned_posts.append(p_safe)

    return render(request, 'post.html', {'posts': cleaned_posts, 'profile': profile})


@login_required
@require_http_methods(['POST'])
def create_post(request):
    # Handle form from post composer (TinyMCE submits HTML content)
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=400)

    title = request.POST.get('title') or (
        request.POST.get('content') or '')[:80]
    content_html = request.POST.get('content') or ''
    # Remove Django template tags from user-submitted content to avoid raw template injection
    content_html = re.sub(r"\{\%[\s\S]*?\%\}", '', content_html)
    content_html = re.sub(r"\{\{[\s\S]*?\}\}", '', content_html)

    # Basic sanitize to ensure saved HTML is safe (server-side)
    allowed_tags = [
        'a', 'abbr', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'p', 'pre',
        'strong', 'ul', 'br', 'hr', 'h1', 'h2', 'h3', 'img'
    ]
    allowed_attrs = {
        'a': ['href', 'title', 'rel', 'target'],
        'img': ['src', 'alt', 'title']
    }
    safe_html = bleach.clean(content_html, tags=allowed_tags, attributes=allowed_attrs, protocols=[
                             'http', 'https', 'data', 'mailto'])
    safe_html = bleach.linkify(safe_html)

    post = Post.objects.create(
        author=profile, title=title[:200], content=safe_html)

    # Handle optional image upload and store using default storage; for now we don't have a Post.image field
    img = request.FILES.get('image')
    if img:
        path = default_storage.save(
            f'posts/{post.id}/{img.name}', ContentFile(img.read()))
        # if Post model later adds an ImageField, we can set it. For now attach a property for template convenience
        post.image_url = default_storage.url(path)

    return redirect(reverse('community'))


@login_required
@require_POST
def toggle_vote(request, post_id):
    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        body = {}
    action = body.get('action')
    profile = get_object_or_404(Profile, user=request.user)
    post = get_object_or_404(Post, id=post_id)

    if action == 'up':
        if profile in post.upvotes.all():
            post.upvotes.remove(profile)
        else:
            post.upvotes.add(profile)
            post.downvotes.remove(profile)
    elif action == 'down':
        if profile in post.downvotes.all():
            post.downvotes.remove(profile)
        else:
            post.downvotes.add(profile)
            post.upvotes.remove(profile)
    else:
        return JsonResponse({'error': 'Invalid action'}, status=400)

    return JsonResponse({'upvotes': post.upvotes.count(), 'downvotes': post.downvotes.count()})


@login_required
@require_POST
def post_comment(request, post_id):
    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        body = {}
    content = (body.get('content') or '').strip()
    # Strip Django template tags from comment content as well
    content = re.sub(r"\{\%[\s\S]*?\%\}", '', content)
    content = re.sub(r"\{\{[\s\S]*?\}\}", '', content)
    if not content:
        return JsonResponse({'error': 'Empty content'}, status=400)

    profile = get_object_or_404(Profile, user=request.user)
    post = get_object_or_404(Post, id=post_id)

    # sanitize incoming HTML/text
    allowed_tags = ['a', 'b', 'blockquote', 'code', 'em',
                    'i', 'li', 'ol', 'p', 'pre', 'strong', 'ul', 'br']
    allowed_attrs = {'a': ['href', 'title', 'rel', 'target']}
    safe_html = bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs, protocols=[
                             'http', 'https', 'mailto'])
    safe_html = bleach.linkify(safe_html)

    comment = Comment.objects.create(
        post=post, author=profile, content=safe_html)

    return JsonResponse({
        'id': comment.id,
        'author': comment.author.user.username,
        'created_at': comment.created_at.strftime('%d %b %Y %H:%M'),
        'content_html': comment.content,
    })


@login_required
@require_POST
def toggle_comment_vote(request, comment_id):
    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        body = {}
    action = body.get('action')
    profile = get_object_or_404(Profile, user=request.user)
    comment = get_object_or_404(Comment, id=comment_id)

    if action == 'up':
        if profile in comment.upvotes.all():
            comment.upvotes.remove(profile)
        else:
            comment.upvotes.add(profile)
            comment.downvotes.remove(profile)
    elif action == 'down':
        if profile in comment.downvotes.all():
            comment.downvotes.remove(profile)
        else:
            comment.downvotes.add(profile)
            comment.upvotes.remove(profile)
    else:
        return JsonResponse({'error': 'Invalid action'}, status=400)

    return JsonResponse({'upvotes': comment.upvotes.count(), 'downvotes': comment.downvotes.count()})


@login_required
def pharmacy(request):
    return render(request, 'pharmacy.html')


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author.user != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    if request.method == 'POST':
        title = request.POST.get('title') or (
            request.POST.get('content') or '')[:80]
        content_html = request.POST.get('content') or ''
        # Remove Django template tags from user-submitted content
        content_html = re.sub(r"\{\%[\s\S]*?\%\}", '', content_html)
        content_html = re.sub(r"\{\{[\s\S]*?\}\}", '', content_html)

        # Basic sanitize
        allowed_tags = [
            'a', 'abbr', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'p', 'pre',
            'strong', 'ul', 'br', 'hr', 'h1', 'h2', 'h3', 'img'
        ]
        allowed_attrs = {
            'a': ['href', 'title', 'rel', 'target'],
            'img': ['src', 'alt', 'title']
        }
        safe_html = bleach.clean(content_html, tags=allowed_tags, attributes=allowed_attrs, protocols=[
                                 'http', 'https', 'data', 'mailto'])
        safe_html = bleach.linkify(safe_html)

        post.title = title[:200]
        post.content = safe_html
        post.save()

        return redirect('community')
    else:
        return render(request, 'edit_post.html', {'post': post})


@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author.user != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    post.delete()
    return redirect('community')


@login_required
def your_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    posts = Post.objects.filter(author=profile).order_by('-created_at')
    comments = Comment.objects.filter(author=profile).order_by('-created_at')
    classifications = Dermal_image.objects.filter(
        user=profile).order_by('-uploaded_at')
    return render(request, 'profile.html', {'profile': profile, 'posts': posts, 'comments': comments, 'classifications': classifications})


@login_required
@csrf_exempt
def predict(request, id):
    image = Dermal_image.objects.get(id=id, user__user=request.user)
    if request.method == "POST":
        drug_history = request.POST.get('drug_history')
        illness_history = request.POST.get('illness_history')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        symptom = request.POST.get('symptom')

        image.drug_history = drug_history
        image.illness_history = illness_history
        image.age = age
        image.gender = gender
        image.symptom = symptom
        image.symptom_en = translate(symptom)
        image.drug_history_en = translate(drug_history)
        image.illness_history_en = translate(illness_history)

        # Call Gemini to analyze
        prompt = f"Phân tích ca da liễu: Bệnh nhân {image.gender}, {image.age}. Dữ liệu đầu vào: Tổn thương da qua ảnh {image.result}, triệu chứng {image.symptom}, tiền sử thuốc {image.drug_history} và bệnh lý {image.illness_history}. Yêu cầu: 1. Đưa ra danh sách các chẩn đoán khả thi (ưu tiên bệnh phổ biến ở người Châu Á), sắp xếp từ nhẹ đến nguy hiểm tính mạng. 2. Làm rõ mối liên hệ giữa tổn thương da với các bệnh lý hệ thống hoặc phản ứng phụ của thuốc bệnh nhân đang dùng. 3. Trình bày dưới dạng danh sách gạch đầu dòng hoặc bảng biểu, ưu tiên ngôn ngữ dễ hiểu, ngắn gọn. (Lưu ý: Kết quả chỉ mang tính chất tham khảo y khoa). "
        reply = call_gemini(prompt, user=request.user)

        # Truncate very long replies to a reasonable size (avoid huge payloads)
        max_len = 16000
        if isinstance(reply, str) and len(reply) > max_len:
            reply = reply[:max_len] + "\n\n...[truncated]"

        # Translate explanation to English
        from .utils import translate_text_gemini
        explain_en = translate_text_gemini(reply, user=request.user)
        
        # Translate user inputs to English
        #image.symptom_en = translate_text_gemini(symptom, user=request.user)
        #image.drug_history_en = translate_text_gemini(drug_history, user=request.user)
        #image.illness_history_en = translate_text_gemini(illness_history, user=request.user)

        # Convert Markdown (if any) to HTML and sanitize it for safe rendering in client
        try:
            raw_html = markdown2.markdown(reply) if isinstance(reply, str) else ''
            
            # Translate markdown explanation if reply was markdown (simplified: translate raw text first then markdown)
            # Actually, `explain_en` is raw text. We need to markdownify it too for display if we want HTML.
            # But the model field `explain_en` is TextField, assuming it stores HTML like `explain`?
            # Creating HTML for English explanation
            raw_html_en = markdown2.markdown(explain_en) if isinstance(explain_en, str) else ''

            allowed_tags = [
                'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'p', 'pre',
                'strong', 'ul', 'br', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
            ]
            allowed_attrs = {
                'a': ['href', 'title', 'rel', 'target']
            }
            
            # Clean Vietnamese HTML
            clean_html = bleach.clean(raw_html, tags=allowed_tags, attributes=allowed_attrs, protocols=['http', 'https', 'mailto'])
            clean_html = bleach.linkify(clean_html)
            
            # Clean English HTML
            clean_html_en = bleach.clean(raw_html_en, tags=allowed_tags, attributes=allowed_attrs, protocols=['http', 'https', 'mailto'])
            clean_html_en = bleach.linkify(clean_html_en)
            
        except Exception:
            clean_html = ''
            clean_html_en = ''

        image.explain = clean_html
        image.explain_en = clean_html_en
        image.save()
        return redirect('result', image_id=image.id)
    
    # Fallback for GET request
    return redirect('result', image_id=id)


def logout_view(request):
    logout(request)
    return redirect('login')
