import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Dashboard Analisis Penyewaan Sepeda",
    layout="wide"
)

st.title("Dashboard Analisis Penyewaan Sepeda")

# Memuat data dari main_data.csv
@st.cache_data
def load_data():
    # Memuat data
    df = pd.read_csv("main_data.csv")
    
    # Berdasarkan contoh data, kita dapat melihat bahwa:
    # - Data harian: kolom yang berakhiran _x (cnt_x, weathersit_x)
    # - Data per jam: kolom yang berakhiran _y (cnt_y, weathersit_y) dengan kolom 'hr'
    
    # Memisahkan data untuk analisis
    # Untuk data harian, kita hanya perlu memilih baris unik berdasarkan tanggal
    day_df = df.drop_duplicates(subset=['dteday'])[['dteday', 'season', 'weathersit_x', 'cnt_x', 'Level_deman']]
    
    # Untuk data per jam, semua baris diperlukan
    hour_df = df[['dteday', 'season', 'hr', 'weathersit_y', 'cnt_y']]
    
    return day_df, hour_df

# Memuat data
try:
    day_df, hour_df = load_data()
    
    # Informasi debugging
    st.sidebar.write("Struktur data:")
    st.sidebar.write(f"- Data harian: {len(day_df)} baris")
    st.sidebar.write(f"- Data per jam: {len(hour_df)} baris")
    
    # Tampilkan contoh data
    with st.sidebar.expander("Lihat contoh data"):
        st.write("Data harian:", day_df.head(3))
        st.write("Data per jam:", hour_df.head(3))
    
    data_loaded = True
except Exception as e:
    st.error(f"Error saat memuat data: {e}")
    st.info("Pastikan file main_data.csv berada dalam direktori yang benar.")
    data_loaded = False

# Lanjutkan dengan dashboard hanya jika data berhasil dimuat
if data_loaded:
    # Sidebar
    st.sidebar.header("Pengaturan Dashboard")
    data_view = st.sidebar.radio("Tampilkan Data:", ["Harian (day)", "Per Jam (hour)", "Keduanya"])

    # Fungsi untuk membuat pie chart musim
    def create_season_pie(df, title, color_palette, count_col):
        summary_df = df.groupby('season')[count_col].sum().reset_index()
        
        # Label
        summary_df['season_label'] = summary_df['season'].map({
            1: 'Spring',
            2: 'Summer',
            3: 'Fall',
            4: 'Winter'
        })
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(summary_df[count_col], labels=summary_df['season_label'], autopct='%1.1f%%', 
               startangle=90, colors=sns.color_palette(color_palette))
        ax.set_title(title)
        ax.axis('equal')
        
        return fig

    # Fungsi untuk membuat bar chart cuaca
    def create_weather_bar(df, title, color_palette, count_col, weather_col):
        # Membuat agregasi data berdasarkan weathersit
        weather_df = df.groupby(weather_col)[count_col].sum().reset_index()
        
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x=weather_col, y=count_col, data=weather_df, palette=color_palette, ax=ax)
        ax.set_xlabel("Cuaca")
        ax.set_ylabel("Total Penyewaan")
        ax.set_title(title)
        
        # Sesuaikan label untuk nilai weathersit
        weather_labels = {
            1: "Cerah",
            2: "Berawan", 
            3: "Hujan", 
            4: "Badai"
        }
        
        # Dapatkan nilai unik untuk weathersit
        weather_values = sorted(weather_df[weather_col].unique())
        ax.set_xticks(range(len(weather_values)))
        ax.set_xticklabels([weather_labels.get(w, f"Cuaca {w}") for w in weather_values])
        
        return fig

    # Layout dashboard berdasarkan pilihan pengguna
    if data_view == "Harian (day)" or data_view == "Keduanya":
        st.header("Analisis Data Harian")
        
        # Membuat layout dengan dua kolom
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribusi Penyewaan Berdasarkan Musim (Harian)")
            season_pie_day = create_season_pie(
                day_df, 
                "Distribusi Penyewaan Sepeda Berdasarkan Musim (day)", 
                "pastel",
                'cnt_x'
            )
            st.pyplot(season_pie_day)
        
        with col2:
            st.subheader("Penyewaan Berdasarkan Cuaca (Harian)")
            weather_bar_day = create_weather_bar(
                day_df, 
                "Grafik penyewaan sepeda berdasarkan cuaca (day)", 
                "Blues",
                'cnt_x',
                'weathersit_x'
            )
            st.pyplot(weather_bar_day)

    if data_view == "Per Jam (hour)" or data_view == "Keduanya":
        st.header("Analisis Data Per Jam")
        
        # Membuat layout dengan dua kolom
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribusi Penyewaan Berdasarkan Musim (Per Jam)")
            season_pie_hour = create_season_pie(
                hour_df, 
                "Distribusi Penyewaan Sepeda Berdasarkan Musim (hour)", 
                "Reds",
                'cnt_y'
            )
            st.pyplot(season_pie_hour)
        
        with col2:
            st.subheader("Penyewaan Berdasarkan Cuaca (Per Jam)")
            weather_bar_hour = create_weather_bar(
                hour_df, 
                "Grafik penyewaan sepeda berdasarkan cuaca (hour)", 
                "Greens",
                'cnt_y',
                'weathersit_y'
            )
            st.pyplot(weather_bar_hour)

    # Tampilkan statistik tambahan
    st.header("Statistik Penyewaan Sepeda")

    # Membuat tabs untuk statistik
    tab1, tab2 = st.tabs(["Statistik Harian", "Statistik Per Jam"])

    with tab1:
        # Menghitung statistik untuk data harian
        total_day = day_df['cnt_x'].sum()
        avg_day = day_df['cnt_x'].mean()
        
        col1, col2 = st.columns(2)
        col1.metric("Total Penyewaan (Harian)", f"{total_day:,}")
        col2.metric("Rata-rata Penyewaan per Hari", f"{avg_day:,.2f}")
        
        # Tampilkan tambahan: Level permintaan
        if 'Level_deman' in day_df.columns:
            st.subheader("Distribusi Level Permintaan")
            fig, ax = plt.subplots(figsize=(8, 5))
            demand_counts = day_df['Level_deman'].value_counts().reset_index()
            demand_counts.columns = ['Level', 'Jumlah']
            sns.barplot(x='Level', y='Jumlah', data=demand_counts, ax=ax, palette="Blues")
            st.pyplot(fig)

    with tab2:
        # Menghitung statistik untuk data per jam
        total_hour = hour_df['cnt_y'].sum()
        avg_hour = hour_df['cnt_y'].mean()
        
        col1, col2 = st.columns(2)
        col1.metric("Total Penyewaan (Per Jam)", f"{total_hour:,}")
        col2.metric("Rata-rata Penyewaan per Jam", f"{avg_hour:,.2f}")
        
        # Tambahan: Distribusi penyewaan per jam
        st.subheader("Distribusi Penyewaan Per Jam")
        hourly_avg = hour_df.groupby('hr')['cnt_y'].mean().reset_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(x='hr', y='cnt_y', data=hourly_avg, marker='o', ax=ax)
        ax.set_xlabel("Jam")
        ax.set_ylabel("Rata-rata Penyewaan")
        ax.set_xticks(range(0, 24))
        ax.set_title("Rata-rata Penyewaan Sepeda per Jam")
        ax.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(fig)

    # Footer
    st.markdown("---")
    st.caption("Dashboard Analisis Penyewaan Sepeda | Dibuat dengan Streamlit")