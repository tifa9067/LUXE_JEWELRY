// ===========================================
// TIVE - ملف JavaScript الرئيسي
// ===========================================

// تهيئة الموقع عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log('TIVE - منصة مجوهرات فاخرة');
    
    // تفعيل مكونات Bootstrap إن وجدت
    initBootstrapComponents();
    
    // تفعيل شريط التنقل
    initNavbar();
    
    // تفعيل البحث
    initSearch();
    
    // تحديث عداد السلة
    updateCartCount();
    
    // تفعيل النماذج
    initForms();
    
    // تفعيل المنتجات
    initProducts();
    
    // تفعيل المعارض
    initGalleries();
    
    // تفعيل تأثيرات التمرير
    initScrollEffects();
    
    // تفعيل الرسائل والتنبيهات
    initMessages();
    
    // تفعيل النماذج الديناميكية
    initDynamicForms();
});

// ===========================================
// 1. مكونات Bootstrap
// ===========================================
function initBootstrapComponents() {
    // تفعيل أدوات التلميح
    if (typeof $ !== 'undefined' && $.fn.tooltip) {
        $('[data-bs-toggle="tooltip"]').tooltip();
        $('[data-bs-toggle="popover"]').popover();
    }
    
    // إغلاق التنبيهات تلقائياً
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 300);
            }
        }, 5000);
    });
}

// ===========================================
// 2. شريط التنقل
// ===========================================
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    const navbarToggle = document.querySelector('.navbar-toggle');
    const navbarMenu = document.querySelector('.navbar-menu');
    
    if (!navbar) return;
    
    // تبديل قائمة التنقل للأجهزة الصغيرة
    if (navbarToggle && navbarMenu) {
        navbarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            navbarMenu.classList.toggle('active');
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-times');
            }
        });
        
        // إغلاق القائمة عند النقر خارجها
        document.addEventListener('click', function(e) {
            if (!navbarToggle.contains(e.target) && !navbarMenu.contains(e.target)) {
                navbarMenu.classList.remove('active');
                const icon = navbarToggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
        });
    }
    
    // تأثيرات التمرير على الشريط
    let lastScroll = 0;
    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;
        
        // إضافة/إزالة تأثير التمرير
        if (currentScroll > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        // إخفاء/إظهار الشريط عند التمرير
        if (currentScroll > lastScroll && currentScroll > 100) {
            navbar.classList.add('navbar-hide');
            navbar.classList.remove('navbar-show');
        } else {
            navbar.classList.remove('navbar-hide');
            navbar.classList.add('navbar-show');
        }
        
        lastScroll = currentScroll;
    });
    
    // تفعيل القوائم المنسدلة
    const dropdowns = document.querySelectorAll('.navbar-dropdown');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('mouseenter', function() {
            this.classList.add('active');
        });
        
        dropdown.addEventListener('mouseleave', function() {
            this.classList.remove('active');
        });
    });
    
    // تفعيل قائمة المستخدم
    const userMenu = document.querySelector('.user-menu');
    if (userMenu) {
        userMenu.addEventListener('mouseenter', function() {
            this.classList.add('active');
        });
        
        userMenu.addEventListener('mouseleave', function() {
            this.classList.remove('active');
        });
    }
}

// ===========================================
// 3. نظام البحث
// ===========================================
function initSearch() {
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');
    
    if (!searchBtn || !searchInput) return;
    
    let searchTimeout;
    
    // تبديل حالة البحث
    searchBtn.addEventListener('click', function(e) {
        e.preventDefault();
        searchInput.classList.toggle('active');
        if (searchInput.classList.contains('active')) {
            searchInput.focus();
        }
    });
    
    // إغلاق البحث عند النقر خارجها
    document.addEventListener('click', function(e) {
        if (!searchBtn.contains(e.target) && !searchInput.contains(e.target)) {
            searchInput.classList.remove('active');
            hideSearchResults();
        }
    });
    
    // البحث أثناء الكتابة
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length > 2) {
            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 500);
        } else {
            hideSearchResults();
        }
    });
    
    // البحث عند الضغط على Enter
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = this.value.trim();
            if (query) {
                window.location.href = `/products/?q=${encodeURIComponent(query)}`;
            }
        }
    });
}

// تنفيذ البحث
function performSearch(query) {
    console.log('البحث عن:', query);
    
    // يمكن استبدال هذا بطلب AJAX حقيقي
    fetch(`/api/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            showSearchResults(data);
        })
        .catch(error => {
            console.error('خطأ في البحث:', error);
        });
}

// عرض نتائج البحث
function showSearchResults(results) {
    hideSearchResults();
    
    if (!results || results.length === 0) return;
    
    const resultsDiv = document.createElement('div');
    resultsDiv.className = 'search-results';
    resultsDiv.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(240, 240, 240, 0.8);
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        margin-top: 10px;
        padding: 1rem;
        z-index: 1000;
        opacity: 0;
        transform: translateY(-10px);
        transition: all 0.3s ease;
    `;
    
    // بناء محتوى النتائج
    let resultsHTML = `
        <div class="search-header" style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(240, 240, 240, 0.5);
        ">
            <span style="font-size: 0.9rem; color: var(--text-gray);">
                نتائج البحث
            </span>
            <a href="/products/" style="
                font-size: 0.8rem;
                color: var(--primary-pastel);
                text-decoration: none;
            ">
                عرض الكل
            </a>
        </div>
        <div class="search-items">
    `;
    
    results.forEach((item, index) => {
        if (index < 5) { // عرض أول 5 نتائج فقط
            resultsHTML += `
                <a href="${item.url}" class="search-item" style="
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    padding: 0.75rem;
                    border-radius: 8px;
                    text-decoration: none;
                    color: var(--text-gray);
                    transition: all 0.2s ease;
                ">
                    <div style="
                        width: 40px;
                        height: 40px;
                        border-radius: 8px;
                        overflow: hidden;
                        background: var(--off-white);
                    ">
                        <img src="${item.image}" alt="${item.name}" style="
                            width: 100%;
                            height: 100%;
                            object-fit: cover;
                        ">
                    </div>
                    <div>
                        <div style="font-size: 0.9rem; color: var(--dark-gray);">${item.name}</div>
                        <div style="font-size: 0.8rem; color: var(--text-light);">${item.price} ر.س</div>
                    </div>
                </a>
            `;
        }
    });
    
    resultsHTML += `</div>`;
    resultsDiv.innerHTML = resultsHTML;
    
    // إضافة النتائج إلى DOM
    const searchContainer = document.querySelector('.search-container');
    if (searchContainer) {
        searchContainer.appendChild(resultsDiv);
        
        // إظهار النتائج مع تأثير
        setTimeout(() => {
            resultsDiv.style.opacity = '1';
            resultsDiv.style.transform = 'translateY(0)';
        }, 10);
        
        // إغلاق النتائج عند النقر خارجها
        document.addEventListener('click', function closeResults(e) {
            if (!searchContainer.contains(e.target) && !searchInput.contains(e.target)) {
                hideSearchResults();
                document.removeEventListener('click', closeResults);
            }
        });
    }
}

// إخفاء نتائج البحث
function hideSearchResults() {
    const existingResults = document.querySelector('.search-results');
    if (existingResults) {
        existingResults.style.opacity = '0';
        existingResults.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            if (existingResults.parentNode) {
                existingResults.remove();
            }
        }, 300);
    }
}

// ===========================================
// 4. نظام السلة
// ===========================================
function updateCartCount() {
    // استخدام jQuery إذا كان موجوداً
    if (typeof $ !== 'undefined') {
        $.ajax({
            url: '/cart/count/',
            method: 'GET',
            success: function(data) {
                updateCartBadge(data.count);
                document.querySelectorAll('.cart-count').forEach(el => {
                    el.textContent = data.count;
                });
            },
            error: function() {
                console.log('خطأ في تحديث عداد السلة');
            }
        });
    } else {
        // استخدام fetch API
        fetch('/cart/count/')
            .then(response => response.json())
            .then(data => {
                updateCartBadge(data.count);
                document.querySelectorAll('.cart-count').forEach(el => {
                    el.textContent = data.count;
                });
            })
            .catch(error => {
                console.log('خطأ في تحديث عداد السلة:', error);
            });
    }
}

// تحديث شارة السلة
function updateCartBadge(count) {
    const cartBtn = document.querySelector('.cart-btn');
    if (!cartBtn) return;
    
    let badge = cartBtn.querySelector('.badge');
    
    if (count > 0) {
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'badge';
            cartBtn.appendChild(badge);
        }
        badge.textContent = count;
        badge.style.animation = 'badgePop 0.3s ease';
        
        // إزالة الأنيميشن بعد التنفيذ
        setTimeout(() => {
            badge.style.animation = '';
        }, 300);
    } else if (badge) {
        badge.remove();
    }
}

// تحديث عنصر في السلة
function updateCartItem(productId, quantity) {
    const csrfToken = getCookie('csrftoken');
    
    fetch(`/cart/update/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount();
            updateCartTotal();
            showMessage('تم تحديث السلة', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('حدث خطأ أثناء تحديث السلة', 'error');
    });
}

// حذف عنصر من السلة
function removeCartItem(productId) {
    if (!confirm('هل تريد إزالة هذا المنتج من السلة؟')) return;
    
    const csrfToken = getCookie('csrftoken');
    
    fetch(`/cart/remove/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const itemElement = document.getElementById(`cart-item-${productId}`);
            if (itemElement) {
                itemElement.style.opacity = '0';
                itemElement.style.transform = 'translateX(-20px)';
                setTimeout(() => {
                    if (itemElement.parentNode) {
                        itemElement.remove();
                    }
                }, 300);
            }
            updateCartCount();
            updateCartTotal();
            showMessage('تمت إزالة المنتج من السلة', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('حدث خطأ أثناء إزالة المنتج', 'error');
    });
}

// تحديث المجموع الكلي
function updateCartTotal() {
    fetch('/cart/total/')
        .then(response => response.json())
        .then(data => {
            document.querySelectorAll('.cart-total').forEach(el => {
                el.textContent = `${data.total} ر.س`;
            });
            document.querySelectorAll('.subtotal').forEach(el => {
                el.textContent = `${data.subtotal} ر.س`;
            });
            document.querySelectorAll('.shipping').forEach(el => {
                el.textContent = `${data.shipping} ر.س`;
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// ===========================================
// 5. نظام النماذج
// ===========================================
function initForms() {
    // منع إرسال النماذج بالضغط على Enter (ما عدا textarea)
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA' && e.target.type !== 'submit') {
                e.preventDefault();
            }
        });
    });
    
    // تأكيد الحذف
    document.querySelectorAll('.confirm-delete').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('هل أنت متأكد من الحذف؟ هذا الإجراء لا يمكن التراجع عنه.')) {
                e.preventDefault();
            }
        });
    });
    
    // تحقق من البريد الإلكتروني
    document.querySelectorAll('input[type="email"]').forEach(input => {
        input.addEventListener('blur', function() {
            const email = this.value.trim();
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailPattern.test(email)) {
                this.classList.add('is-invalid');
                let feedback = this.nextElementSibling;
                if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                    feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    feedback.textContent = 'يرجى إدخال بريد إلكتروني صحيح';
                    this.parentNode.appendChild(feedback);
                }
            } else {
                this.classList.remove('is-invalid');
                const feedback = this.nextElementSibling;
                if (feedback && feedback.classList.contains('invalid-feedback')) {
                    feedback.remove();
                }
            }
        });
    });
}

// ===========================================
// 6. نظام المنتجات
// ===========================================
function initProducts() {
    // إضافة/إزالة من المفضلة
    document.querySelectorAll('.wishlist-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const csrfToken = getCookie('csrftoken');
            
            if (!productId) return;
            
            fetch(`/wishlist/toggle/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                const icon = this.querySelector('i');
                if (icon) {
                    if (data.added) {
                        icon.classList.remove('far', 'fa-heart');
                        icon.classList.add('fas', 'fa-heart', 'text-danger');
                        showMessage('تمت الإضافة إلى المفضلة', 'success');
                    } else {
                        icon.classList.remove('fas', 'fa-heart', 'text-danger');
                        icon.classList.add('far', 'fa-heart');
                        showMessage('تمت الإزالة من المفضلة', 'info');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('يرجى تسجيل الدخول أولاً', 'warning');
            });
        });
    });
    
    // إضافة إلى السلة
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const csrfToken = getCookie('csrftoken');
            formData.append('csrfmiddlewaretoken', csrfToken);
            
            fetch(this.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCartCount();
                    showMessage('تمت الإضافة إلى السلة', 'success');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('حدث خطأ أثناء الإضافة للسلة', 'error');
            });
        });
    });
    
    // تحكم بالكمية
    document.querySelectorAll('.quantity-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.closest('.quantity-selector').querySelector('.quantity-input');
            if (!input) return;
            
            let value = parseInt(input.value) || 0;
            const min = parseInt(input.min) || 1;
            const max = parseInt(input.max) || 99;
            
            if (this.classList.contains('decrease')) {
                if (value > min) {
                    input.value = value - 1;
                }
            } else if (this.classList.contains('increase')) {
                if (value < max) {
                    input.value = value + 1;
                }
            }
            
            // تفعيل حدث change
            input.dispatchEvent(new Event('change', { bubbles: true }));
        });
    });
}

// ===========================================
// 7. المعارض والصور
// ===========================================
function initGalleries() {
    // معرض الصور المصغرة
    document.querySelectorAll('.gallery-thumbnail').forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            const mainImageUrl = this.dataset.image || this.querySelector('img').src;
            const mainImage = document.querySelector('.gallery-main img');
            
            if (mainImage && mainImageUrl) {
                // إضافة تأثير تغيير الصورة
                mainImage.style.opacity = '0';
                setTimeout(() => {
                    mainImage.src = mainImageUrl;
                    mainImage.style.opacity = '1';
                }, 150);
                
                // تحديث الصورة النشطة
                document.querySelectorAll('.gallery-thumbnail').forEach(t => {
                    t.classList.remove('active');
                });
                this.classList.add('active');
            }
        });
    });
    
    // تكبير الصور
    document.querySelectorAll('.zoomable-image').forEach(img => {
        img.addEventListener('click', function() {
            openLightbox(this.src);
        });
    });
}

// فتح معرض الصور
function openLightbox(imgSrc) {
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2000;
        opacity: 0;
        transition: opacity 0.3s ease;
        backdrop-filter: blur(10px);
    `;
    
    const img = document.createElement('img');
    img.src = imgSrc;
    img.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        border-radius: var(--radius-md);
        transform: scale(0.9);
        transition: transform 0.3s ease;
        cursor: zoom-out;
    `;
    
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '×';
    closeBtn.style.cssText = `
        position: absolute;
        top: 20px;
        right: 20px;
        background: none;
        border: none;
        color: white;
        font-size: 2rem;
        cursor: pointer;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2001;
    `;
    
    lightbox.appendChild(img);
    lightbox.appendChild(closeBtn);
    document.body.appendChild(lightbox);
    
    // إظهار المعرض مع تأثير
    setTimeout(() => {
        lightbox.style.opacity = '1';
        img.style.transform = 'scale(1)';
    }, 10);
    
    // إغلاق المعرض
    function closeLightbox() {
        lightbox.style.opacity = '0';
        img.style.transform = 'scale(0.9)';
        setTimeout(() => {
            if (lightbox.parentNode) {
                document.body.removeChild(lightbox);
            }
        }, 300);
    }
    
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox || e.target === closeBtn) {
            closeLightbox();
        }
    });
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeLightbox();
        }
    });
}

// ===========================================
// 8. تأثيرات التمرير
// ===========================================
function initScrollEffects() {
    // تأثيرات الفيد إن
    const fadeElements = document.querySelectorAll('.fade-in');
    
    const fadeInObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    fadeElements.forEach(element => {
        fadeInObserver.observe(element);
    });
    
    // تأثيرات البطاقات
    const cards = document.querySelectorAll('.glass-card, .product-card');
    
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, {
        threshold: 0.1
    });
    
    cards.forEach(card => {
        cardObserver.observe(card);
    });
    
    // التمرير السلس للروابط الداخلية
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ===========================================
// 9. نظام الرسائل والتنبيهات
// ===========================================
function initMessages() {
    // لا يوجد حاجة لتهيئة إضافية
}

// عرض رسالة للمستخدم
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `tive-message message-${type}`;
    messageDiv.innerHTML = `
        <i class="fas ${getMessageIcon(type)} me-2"></i>
        <span>${message}</span>
        <button class="message-close"><i class="fas fa-times"></i></button>
    `;
    
    messageDiv.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: white;
        padding: 1rem 1.5rem;
        border-radius: var(--radius-md);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        z-index: 2000;
        transform: translateX(120%);
        transition: transform 0.3s ease;
        max-width: 300px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-right: 3px solid ${getMessageColor(type)};
    `;
    
    document.body.appendChild(messageDiv);
    
    // إظهار الرسالة
    setTimeout(() => {
        messageDiv.style.transform = 'translateX(0)';
    }, 10);
    
    // زر الإغلاق
    const closeBtn = messageDiv.querySelector('.message-close');
    closeBtn.addEventListener('click', function() {
        messageDiv.style.transform = 'translateX(120%)';
        setTimeout(() => {
            if (messageDiv.parentNode) {
                document.body.removeChild(messageDiv);
            }
        }, 300);
    });
    
    // إزالة تلقائية بعد 5 ثواني
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.style.transform = 'translateX(120%)';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    document.body.removeChild(messageDiv);
                }
            }, 300);
        }
    }, 5000);
}

// الحصول على أيقونة الرسالة
function getMessageIcon(type) {
    const icons = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };
    return icons[type] || 'fa-info-circle';
}

// الحصول على لون الرسالة
function getMessageColor(type) {
    const colors = {
        'success': 'var(--accent-pastel)',
        'error': '#ff6b6b',
        'warning': '#ffc107',
        'info': 'var(--secondary-pastel)'
    };
    return colors[type] || 'var(--text-light)';
}

// ===========================================
// 10. النماذج الديناميكية
// ===========================================
function initDynamicForms() {
    // تحميل النماذج الديناميكية
    document.querySelectorAll('[data-load-form]').forEach(btn => {
        btn.addEventListener('click', function() {
            const url = this.dataset.loadForm;
            const containerId = this.dataset.target;
            
            if (url && containerId) {
                loadForm(url, containerId);
            }
        });
    });
    
    // تفعيل السحب والإفلات للملفات
    const dropAreas = document.querySelectorAll('.drop-area');
    dropAreas.forEach(area => {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            area.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            area.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            area.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            area.classList.add('highlight');
        }
        
        function unhighlight() {
            area.classList.remove('highlight');
        }
        
        area.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files, area);
        }
    });
}

// تحميل نموذج
function loadForm(url, containerId) {
    fetch(url)
        .then(response => response.text())
        .then(html => {
            const container = document.querySelector(containerId);
            if (container) {
                container.innerHTML = html;
                initForms(); // إعادة تهيئة النماذج
            }
        })
        .catch(error => {
            console.error('Error loading form:', error);
        });
}

// معالجة الملفات المسقطة
function handleFiles(files, dropArea) {
    const file = files[0];
    if (!file) return;
    
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = dropArea.querySelector('.image-preview') || 
                           document.getElementById('imagePreview');
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
            
            // تخزين البيانات في حقل مخفي
            const hiddenInput = dropArea.querySelector('input[type="hidden"]');
            if (hiddenInput) {
                hiddenInput.value = e.target.result;
            }
        };
        reader.readAsDataURL(file);
        
        showMessage('تم رفع الصورة بنجاح', 'success');
    } else {
        showMessage('يرجى رفع صورة فقط', 'error');
    }
}

// ===========================================
// 11. وظائف مساعدة
// ===========================================
// الحصول على قيمة cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// تنسيق الأرقام
function formatNumber(num) {
    return new Intl.NumberFormat('ar-SA').format(num);
}

// تنسيق التاريخ
function formatDate(date) {
    return new Date(date).toLocaleDateString('ar-SA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// ===========================================
// 12. CSS ديناميكي إضافي
// ===========================================
const dynamicStyles = document.createElement('style');
dynamicStyles.textContent = `
    /* تأثيرات الفيد إن */
    .fade-in {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.6s ease, transform 0.6s ease;
    }
    
    .fade-in.visible {
        opacity: 1;
        transform: translateY(0);
    }
    
    /* تأثيرات البطاقات */
    .glass-card, .product-card {
        transition: all 0.3s ease;
    }
    
    .glass-card.animated, .product-card.animated {
        animation: cardFloat 0.6s ease;
    }
    
    @keyframes cardFloat {
        0% {
            transform: translateY(20px);
            opacity: 0;
        }
        100% {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    /* تأثير شارة السلة */
    @keyframes badgePop {
        0% {
            transform: scale(0);
            opacity: 0;
        }
        70% {
            transform: scale(1.2);
            opacity: 1;
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    /* منطقة السحب والإفلات */
    .drop-area.highlight {
        border-color: var(--primary-pastel);
        background-color: rgba(255, 183, 197, 0.05);
    }
    
    /* تحسينات للاستجابة */
    @media (max-width: 768px) {
        .tive-message {
            max-width: calc(100% - 40px);
            left: 20px;
            right: 20px;
        }
    }
`;
document.head.appendChild(dynamicStyles);

// ===========================================
// التصدير للاستخدام في ملفات أخرى
// ===========================================
window.TIVE = {
    showMessage: showMessage,
    updateCartCount: updateCartCount,
    updateCartItem: updateCartItem,
    removeCartItem: removeCartItem,
    openLightbox: openLightbox,
    formatNumber: formatNumber,
    formatDate: formatDate
};

console.log('TIVE JavaScript loaded successfully!');