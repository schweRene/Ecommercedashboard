import pandas as pd
import streamlit as st
import plotly.express as px


def load_data():
    file_path = "ecommerce_sales.csv"
    df = pd.read_csv(file_path)
    
    # Exaktes Mapping basierend auf deiner CSV-Struktur
    category_mapping = {
        "Home": "Haus",
        "Grocery": "Lebensmittel",
        "Electronics": "Elektronik",
        "Beauty": "Beauty",
        "Toys": "Spielzeug",
        "Sports": "Sport"
    }
    
    payment_mapping = {
        "Credit Card": "Kreditkarte",
        "UPI": "Überweisung (UPI)",
        "COD": "Nachnahme (COD)",
        "Debit Card": "Debitkarte",
        "Net Banking": "Online-Banking"
    }
    
    # Anwendung des Mappings
    df['category'] = df['category'].replace(category_mapping)
    df['payment_method'] = df['payment_method'].replace(payment_mapping)
    
    # Datum und Retouren
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    if df['returned'].dtype == 'object':
        df['returned'] = df['returned'].str.strip().str.lower() == 'yes'
    
    return df

def get_key_metrics(df):
    total_sales = df['total_amount'].sum()
    total_profit = df['profit_margin'].sum()
    total_orders = len(df)
    aov = total_sales / total_orders if total_orders > 0 else 0
    return total_sales, total_profit, total_orders, aov

def format_german(number):
    return f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def get_filter_options(df):
    categories = sorted(df['category'].unique().tolist())
    regions = sorted(df['region'].unique().tolist())
    years = sorted(df['order_date'].dt.year.unique().tolist(), reverse=True)
    return categories, regions, years

def create_year_vergleich_chart(df):
    yearly_data = df.groupby(df['order_date'].dt.year)['total_amount'].sum().reset_index()
    yearly_data.columns = ['Jahr', 'Umsatz']
    fig = px.bar(
        yearly_data, x='Jahr', y='Umsatz', text='Umsatz', 
        title="<b>Umsatzentwicklung im Jahresvergleich</b>",
        template="plotly_white", color_discrete_sequence=['#0083B8'] 
    )
    fig.update_traces(
        texttemplate='%{y:,.0f} €', textposition='outside',
        cliponaxis=False, textfont=dict(color='#000000', size=14)
    )
    fig.update_layout(
        separators=",.", paper_bgcolor='white', plot_bgcolor='white',
        font=dict(color='#000000', family="Arial"), title_font=dict(color='#000000', size=16),
        xaxis=dict(type='category', title=None, tickfont=dict(color='#000000', size=13), linecolor='#000000'),
        yaxis=dict(showgrid=True, gridcolor='lightgray', title=None, tickformat=",.0f", tickfont=dict(color='#000000', size=13)),
        margin=dict(t=60, l=10, r=10, b=10)
    )
    return fig

# NEU: Die Funktion für das Kuchendiagramm
def create_umsatz_anteil_chart(df, selected_year):
    df_year = df[df['order_date'].dt.year == selected_year]
    cat_data = df_year.groupby('category')['total_amount'].sum().reset_index()
    fig = px.pie(
        cat_data, values='total_amount', names='category',
        title=f"<b>Umsatzverteilung {selected_year}</b>",
        hole=0.4, color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig.update_traces(
        textinfo='percent+label', textfont=dict(color='#000000', size=12),
        marker=dict(line=dict(color='#000000', width=1))
    )
    fig.update_layout(
        separators=",.", paper_bgcolor='white', font=dict(color='#000000', family="Arial"),
        title_font=dict(color='#000000', size=20), margin=dict(t=50, b=20, l=20, r=20)
    )
    return fig

def create_monatsanalyse_chart(df, selected_year):
    
    # Daten für ausgewähltes Jahr
    df_year = df[df['order_date'].dt.year == selected_year].copy()

    # Monatsnummer (nur für Sortierung, NICHT sichtbar)
    df_year['monat_num'] = df_year['order_date'].dt.month

    # Deutsche Monatsnamen (explizit, ohne locale)
    monate_de = {
        1: "Januar", 2: "Februar", 3: "März", 4: "April",
        5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
        9: "September", 10: "Oktober", 11: "November", 12: "Dezember"
    }

    # Deutscher Monatsname
    df_year['Monat'] = df_year['monat_num'].map(monate_de)

    # Umsatz pro Monat und Kategorie (korrekt sortiert)
    cat_monthly = (
        df_year
        .groupby(['monat_num', 'Monat', 'category'])['total_amount']
        .sum()
        .reset_index()
        .sort_values('monat_num')
    )

    # Stapeldiagramm
    fig = px.bar(
        cat_monthly,
        x='Monat',
        y='total_amount',
        color='category',
        title=f"<b>Monatlicher Umsatz nach Kategorien ({selected_year})</b>",
        template="plotly_white",
        barmode='stack',
        color_discrete_sequence=px.colors.qualitative.Prism
    )

    fig.update_layout(
        separators=",.",
        font=dict(color='#000000', family="Arial"),
        title_font=dict(color='#000000', size=16),
        xaxis=dict(
            title=None,
            tickfont=dict(color='#000000', size=12),
            linecolor='#000000'
        ),
        yaxis=dict(
            title="Umsatz in €",
            tickfont=dict(color='#000000'),
            gridcolor='lightgray'
        ),
        legend=dict(
            title=dict(text="<b>Kategorie</b>", font=dict(color='#000000')),
            font=dict(color='#000000'),
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        ),
        margin=dict(t=80, l=10, r=10, b=10)
    )

    return fig


def main():
    st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")
    
    # CSS: Verkleinert gezielt NUR die Zahlen-Werte der Metrics
    st.markdown("""
        <style>
        [data-testid="stMetricValue"] {
            font-size: 24px !important;
            color: #000000 !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("🛍️ Analyse E-Commerce-Geschäft")

    df = load_data()
    #st.sidebar.header("Filtereinstellungen")
    cats, regs, yrs = get_filter_options(df)
    selected_year = st.sidebar.selectbox("Jahr", yrs, index=0)
    selected_regs = st.sidebar.multiselect("Regionen", regs, default=[])
    selected_cats = st.sidebar.multiselect("Kategorien", cats, default=[])

    mask_trend = pd.Series(True, index=df.index)
    if selected_regs: mask_trend &= df['region'].isin(selected_regs)
    if selected_cats: mask_trend &= df['category'].isin(selected_cats)
    df_trend = df[mask_trend]

    mask_detail = mask_trend & (df['order_date'].dt.year == selected_year)
    df_filtered = df[mask_detail]

    # --- KPI BEREICH ---
    sales, profit, orders, aov = get_key_metrics(df_filtered)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric(f"Umsatz ({selected_year})", f"{format_german(sales)} €")
    with col2: st.metric(f"Profit ({selected_year})", f"{format_german(profit)} €")
    with col3: st.metric(f"Bestellungen ({selected_year})", f"{orders:,.0f}".replace(",", "."))
    with col4: st.metric(f"Ø-Bestellwert ({selected_year})", f"{format_german(aov)} €")

    st.divider()

    # --- DIAGRAMM BEREICH (Jetzt mit Kuchendiagramm daneben) ---
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(create_year_vergleich_chart(df_trend), use_container_width=True)
    with chart_col2:
        # Hier wird das Kuchendiagramm aufgerufen
        st.plotly_chart(create_umsatz_anteil_chart(df_trend, selected_year), use_container_width=True)
    
    st.divider()

    st.plotly_chart(create_monatsanalyse_chart(df, selected_year), use_container_width=True)
    st.divider()

    # --- TABELLEN BEREICH ---
    st.subheader(f"Transaktionen {selected_year}")
    display_columns = {"order_date": "Datum", "category": "Kategorie", "region": "Region", "total_amount": "Umsatz in €", "profit_margin": "Gewinn in €", "payment_method": "Zahlungsart", "returned": "Retoure"}
    
    st.dataframe(
        df_filtered[[
            "order_date", "category", "region", "total_amount", 
            "profit_margin", "payment_method", "returned"
        ]], 
        hide_index=True, 
        use_container_width=True,
        height="content", 
        column_config={
            "order_date": st.column_config.DateColumn("Datum", format="DD.MM.YYYY"),
            "category": "Kategorie",
            "region": "Region",
            "total_amount": st.column_config.NumberColumn("Umsatz in €", format="%.2f"),
            "profit_margin": st.column_config.NumberColumn("Gewinn in €", format="%.2f"),
            "payment_method": "Zahlungsart",
            "returned": "Retoure"
        }
    )

    

if __name__ == "__main__":
    main()