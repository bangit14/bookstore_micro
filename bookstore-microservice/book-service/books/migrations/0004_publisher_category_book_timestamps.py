import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_book_description_book_isbn'),
    ]

    operations = [
        # 1. Create books_publisher table
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('address', models.TextField(blank=True, default='')),
                ('phone', models.CharField(blank=True, default='', max_length=20)),
                ('email', models.EmailField(blank=True, default='', max_length=254)),
                ('website', models.URLField(blank=True, default='')),
                ('description', models.TextField(blank=True, default='')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Publisher',
                'verbose_name_plural': 'Publishers',
                'ordering': ['name'],
            },
        ),
        # 2. Create books_category table
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    choices=[
                        ('VH_VIET', 'Văn Học Việt Nam'),
                        ('VH_NUOC_NGOAI', 'Văn Học Nước Ngoài'),
                        ('VH_DANG_DAI', 'Văn Học Đương Đại'),
                        ('VH_CO_DIEN', 'Văn Học Cổ Điển'),
                        ('TIEU_THUYET', 'Tiểu Thuyết'),
                        ('TRUYEN_NGAN', 'Truyện Ngắn'),
                        ('THO_CA', 'Thơ Ca'),
                        ('KY_SU', 'Ký Sự - Tùy Bút'),
                        ('KINH_TE', 'Kinh Tế'),
                        ('KINH_DOANH', 'Kinh Doanh - Khởi Nghiệp'),
                        ('MARKETING', 'Marketing - Bán Hàng'),
                        ('QUAN_TRI', 'Quản Trị - Lãnh Đạo'),
                        ('TAI_CHINH', 'Tài Chính - Đầu Tư'),
                        ('KE_TOAN', 'Kế Toán - Kiểm Toán'),
                        ('KY_NANG_SONG', 'Kỹ Năng Sống'),
                        ('TU_DUY', 'Tư Duy - Logic'),
                        ('GIAO_TIEP', 'Giao Tiếp - Ứng Xử'),
                        ('LANH_DAO', 'Lãnh Đạo - Quản Lý'),
                        ('PHAT_TRIEN_BAN_THAN', 'Phát Triển Bản Thân'),
                        ('NGOAI_NGU', 'Ngoại Ngữ'),
                        ('CNTT', 'Công Nghệ Thông Tin'),
                        ('LAP_TRINH', 'Lập Trình - Programming'),
                        ('KHOA_HOC_TU_NHIEN', 'Khoa Học Tự Nhiên'),
                        ('TOAN_HOC', 'Toán Học'),
                        ('VAT_LY', 'Vật Lý'),
                        ('HOA_HOC', 'Hóa Học'),
                        ('SINH_HOC', 'Sinh Học'),
                        ('CONG_NGHE', 'Công Nghệ - Kỹ Thuật'),
                        ('LICH_SU', 'Lịch Sử'),
                        ('TRIET_HOC', 'Triết Học'),
                        ('TAM_LY_HOC', 'Tâm Lý Học'),
                        ('XA_HOI_HOC', 'Xã Hội Học'),
                        ('CHINH_TRI', 'Chính Trị - Pháp Luật'),
                        ('TON_GIAO', 'Tôn Giáo - Tâm Linh'),
                        ('GIAO_KHOA', 'Sách Giáo Khoa'),
                        ('THAM_KHAO', 'Sách Tham Khảo'),
                        ('LUYEN_THI', 'Luyện Thi - Ôn Tập'),
                        ('GIAO_DUC', 'Giáo Dục - Đào Tạo'),
                        ('THIEU_NHI', 'Thiếu Nhi'),
                        ('TRUYEN_TRANH', 'Truyện Tranh - Comic'),
                        ('DO_CHOI', 'Đồ Chơi - Học Liệu'),
                        ('NUOI_DAY_CON', 'Nuôi Dạy Con'),
                        ('NGHE_THUAT', 'Nghệ Thuật'),
                        ('DIEN_ANH', 'Điện Ảnh - Sân Khấu'),
                        ('AM_NHAC', 'Âm Nhạc'),
                        ('HOI_HUA', 'Hội Họa - Mỹ Thuật'),
                        ('NHIEP_ANH', 'Nhiếp Ảnh'),
                        ('THOI_TRANG', 'Thời Trang - Làm Đẹp'),
                        ('SUC_KHOE', 'Sức Khỏe'),
                        ('Y_HOC', 'Y Học - Dược'),
                        ('LAM_DEP', 'Làm Đẹp'),
                        ('NHA_CUA', 'Nhà Cửa - Trang Trí'),
                        ('NAU_AN', 'Nấu Ăn - Ẩm Thực'),
                        ('DU_LICH', 'Du Lịch - Phượt'),
                        ('THE_THAO', 'Thể Thao - Yoga'),
                        ('TRUYEN_TRINH_THAM', 'Trinh Thám - Kinh Dị'),
                        ('HUYEN_BI', 'Huyền Bí - Phiêu Lưu'),
                        ('LANG_MAN', 'Lãng Mạn'),
                        ('TU_DIEN', 'Từ Điển - Bách Khoa'),
                        ('CONG_CU_SACH', 'Công Cụ Sách'),
                        ('KHAC', 'Khác'),
                    ],
                    max_length=100,
                    unique=True,
                )),
                ('display_name', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('icon', models.CharField(blank=True, default='bi-bookmark', max_length=50)),
                ('color', models.CharField(blank=True, default='#0288d1', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['order', 'name'],
            },
        ),
        # 3. Add publisher FK to books_book (nullable)
        migrations.AddField(
            model_name='book',
            name='publisher',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='books',
                to='books.publisher',
            ),
        ),
        # 4. Add category FK to books_book (nullable)
        migrations.AddField(
            model_name='book',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='books',
                to='books.category',
            ),
        ),
        # 5. Add created_at (use default for existing rows, preserve_default=False removes default after migration)
        migrations.AddField(
            model_name='book',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        # 6. Add updated_at
        migrations.AddField(
            model_name='book',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
