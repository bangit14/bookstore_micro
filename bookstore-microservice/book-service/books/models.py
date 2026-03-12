from django.db import models


class Publisher(models.Model):
    """Nhà xuất bản"""
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    website = models.URLField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Publisher'
        verbose_name_plural = 'Publishers'

    def __str__(self):
        return self.name


class Category(models.Model):
    """Thể loại sách"""
    
    # Enum-like choices cho category
    CATEGORY_CHOICES = [
        # Văn học
        ('VH_VIET', 'Văn Học Việt Nam'),
        ('VH_NUOC_NGOAI', 'Văn Học Nước Ngoài'),
        ('VH_DANG_DAI', 'Văn Học Đương Đại'),
        ('VH_CO_DIEN', 'Văn Học Cổ Điển'),
        ('TIEU_THUYET', 'Tiểu Thuyết'),
        ('TRUYEN_NGAN', 'Truyện Ngắn'),
        ('THO_CA', 'Thơ Ca'),
        ('KY_SU', 'Ký Sự - Tùy Bút'),
        
        # Kinh tế - Kinh doanh
        ('KINH_TE', 'Kinh Tế'),
        ('KINH_DOANH', 'Kinh Doanh - Khởi Nghiệp'),
        ('MARKETING', 'Marketing - Bán Hàng'),
        ('QUAN_TRI', 'Quản Trị - Lãnh Đạo'),
        ('TAI_CHINH', 'Tài Chính - Đầu Tư'),
        ('KE_TOAN', 'Kế Toán - Kiểm Toán'),
        
        # Kỹ năng
        ('KY_NANG_SONG', 'Kỹ Năng Sống'),
        ('TU_DUY', 'Tư Duy - Logic'),
        ('GIAO_TIEP', 'Giao Tiếp - Ứng Xử'),
        ('LANH_DAO', 'Lãnh Đạo - Quản Lý'),
        ('PHAT_TRIEN_BAN_THAN', 'Phát Triển Bản Thân'),
        ('NGOAI_NGU', 'Ngoại Ngữ'),
        
        # Khoa học - Công nghệ
        ('CNTT', 'Công Nghệ Thông Tin'),
        ('LAP_TRINH', 'Lập Trình - Programming'),
        ('KHOA_HOC_TU_NHIEN', 'Khoa Học Tự Nhiên'),
        ('TOAN_HOC', 'Toán Học'),
        ('VAT_LY', 'Vật Lý'),
        ('HOA_HOC', 'Hóa Học'),
        ('SINH_HOC', 'Sinh Học'),
        ('CONG_NGHE', 'Công Nghệ - Kỹ Thuật'),
        
        # Xã hội - Nhân văn
        ('LICH_SU', 'Lịch Sử'),
        ('TRIET_HOC', 'Triết Học'),
        ('TAM_LY_HOC', 'Tâm Lý Học'),
        ('XA_HOI_HOC', 'Xã Hội Học'),
        ('CHINH_TRI', 'Chính Trị - Pháp Luật'),
        ('TON_GIAO', 'Tôn Giáo - Tâm Linh'),
        
        # Giáo dục
        ('GIAO_KHOA', 'Sách Giáo Khoa'),
        ('THAM_KHAO', 'Sách Tham Khảo'),
        ('LUYEN_THI', 'Luyện Thi - Ôn Tập'),
        ('GIAO_DUC', 'Giáo Dục - Đào Tạo'),
        
        # Thiếu nhi
        ('THIEU_NHI', 'Thiếu Nhi'),
        ('TRUYEN_TRANH', 'Truyện Tranh - Comic'),
        ('DO_CHOI', 'Đồ Chơi - Học Liệu'),
        ('NUOI_DAY_CON', 'Nuôi Dạy Con'),
        
        # Nghệ thuật - Giải trí
        ('NGHE_THUAT', 'Nghệ Thuật'),
        ('DIEN_ANH', 'Điện Ảnh - Sân Khấu'),
        ('AM_NHAC', 'Âm Nhạc'),
        ('HOI_HUA', 'Hội Họa - Mỹ Thuật'),
        ('NHIEP_ANH', 'Nhiếp Ảnh'),
        ('THOI_TRANG', 'Thời Trang - Làm Đẹp'),
        
        # Sức khỏe - Đời sống
        ('SUC_KHOE', 'Sức Khỏe'),
        ('Y_HOC', 'Y Học - Dược'),
        ('LAM_DEP', 'Làm Đẹp'),
        ('NHA_CUA', 'Nhà Cửa - Trang Trí'),
        ('NAU_AN', 'Nấu Ăn - Ẩm Thực'),
        ('DU_LICH', 'Du Lịch - Phượt'),
        ('THE_THAO', 'Thể Thao - Yoga'),
        
        # Khác
        ('TRUYEN_TRINH_THAM', 'Trinh Thám - Kinh Dị'),
        ('HUYEN_BI', 'Huyền Bí - Phiêu Lưu'),
        ('LANG_MAN', 'Lãng Mạn'),
        ('TU_DIEN', 'Từ Điển - Bách Khoa'),
        ('CONG_CU_SACH', 'Công Cụ Sách'),
        ('KHAC', 'Khác'),
    ]
    
    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES, unique=True)
    display_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, default="")
    icon = models.CharField(max_length=50, blank=True, default="bi-bookmark")
    color = models.CharField(max_length=20, blank=True, default="#0288d1")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.get_name_display()
    
    def save(self, *args, **kwargs):
        # Auto-populate display_name from choices if not provided
        if not self.display_name:
            self.display_name = self.get_name_display()
        super().save(*args, **kwargs)


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, blank=True, default="")
    image_url = models.URLField(blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    description = models.TextField(blank=True, default="")
    
    # Foreign keys
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return self.title
