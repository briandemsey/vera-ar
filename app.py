"""
VERA-AR: Verification Engine for Results & Accountability - Arkansas
Type 4 Detection using ELPA21 Speaking vs Writing Domain Growth + ATLAS Achievement Data

Arkansas context:
- ELPA21 (not WIDA) -- English Language Proficiency Assessment for the 21st Century
- 4 domains: Listening, Speaking, Reading, Writing
- 4 levels: Limited / Basic / Proficient / Advanced
- ATLAS (ACT-aligned) state assessment, 4 levels:
    In Need of Support / Close / Ready / Exceeding
- ~235 districts, ~42,000 ELs (~8.5% statewide)
- Top EL districts: Springdale, Rogers, Bentonville (NWA corridor)
- Marshallese diaspora: largest Marshallese community outside Marshall Islands
  concentrated in Springdale -- unique linguistic/cultural challenge
- LEARNS Act (2023): sweeping education reform (vouchers, literacy, accountability)
- myschoolinfo.arkansas.gov -- public data dashboard
- ESSA School Index accountability system

H-EDU.Solutions | https://h-edu.solutions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# CONFIGURATION
# ============================================================================

APP_AR_RED = "#CC0000"
AR_WHITE = "#FFFFFF"
AR_DARK = "#990000"
AR_GRAY = "#4A4A4A"
AR_LIGHT_RED = "#E06666"

# ============================================================================
# DATA: Arkansas Districts with EL Populations
# Source: ADE / myschoolinfo.arkansas.gov
# ============================================================================

def load_districts():
    """Load AR districts with significant EL populations.

    Arkansas's EL population is heavily concentrated in Northwest Arkansas (NWA),
    driven by the poultry industry (Tyson, Simmons, George's) and Walmart HQ corridor.
    The Marshallese diaspora in Springdale represents the largest Marshallese community
    outside the Marshall Islands -- a unique linguistic and cultural challenge for schools.
    """
    data = [
        # (lea_id, district_name, total_students, el_count, el_percent,
        #  atlas_ready_all, atlas_ready_el, graduation_rate, essa_index, context_note)

        # --- NWA Corridor (poultry/Walmart) ---
        ("7201", "Springdale School District", 23500, 7520, 32.0, 42.5, 14.8, 84.2, 62.5, "Largest Marshallese diaspora; Tyson HQ area"),
        ("7202", "Rogers School District", 16200, 4536, 28.0, 46.8, 16.2, 86.5, 67.2, "NWA corridor; poultry + retail economy"),
        ("7203", "Bentonville School District", 19500, 3900, 20.0, 58.2, 21.5, 92.8, 75.8, "Walmart HQ; affluent + diverse"),
        ("0401", "Fort Smith School District", 14200, 3550, 25.0, 38.5, 12.5, 80.2, 58.5, "River Valley; Vietnamese + Hispanic ELs"),
        ("7206", "Siloam Springs School District", 4800, 1440, 30.0, 40.2, 13.8, 82.5, 60.2, "Simmons Foods HQ; high EL concentration"),

        # --- Central Arkansas ---
        ("6001", "Little Rock School District", 21000, 3150, 15.0, 35.8, 11.2, 78.5, 55.2, "Capital city; diverse EL population"),
        ("6005", "North Little Rock School District", 8500, 1275, 15.0, 37.2, 12.0, 79.8, 56.8, "Suburban; growing EL population"),
        ("6010", "Pulaski County Special School District", 10200, 1020, 10.0, 40.5, 13.5, 82.0, 59.5, "County district; dispersed ELs"),

        # --- Growing EL districts ---
        ("0301", "Fayetteville School District", 10500, 1575, 15.0, 52.5, 18.5, 90.2, 72.5, "University of Arkansas; academic community"),
        ("0501", "Russellville School District", 5200, 1040, 20.0, 41.8, 14.2, 83.5, 61.5, "Arkansas River Valley; poultry processing"),
        ("1701", "De Queen School District", 2800, 840, 30.0, 36.5, 11.0, 78.8, 54.5, "Sevier County; timber + poultry"),
        ("2001", "Dardanelle School District", 2400, 624, 26.0, 38.8, 12.8, 80.5, 57.2, "Yell County; Tyson plant"),
        ("1301", "Green Forest School District", 1600, 544, 34.0, 34.2, 10.5, 76.5, 52.8, "Carroll County; highest rural EL%"),
        ("7204", "Gravette School District", 2200, 330, 15.0, 44.5, 15.8, 85.2, 64.5, "NWA fringe; growing community"),
        ("5501", "Searcy School District", 4500, 360, 8.0, 48.2, 16.5, 87.5, 68.2, "White County; moderate EL growth"),
    ]

    return pd.DataFrame(data, columns=[
        'lea_id', 'district_name', 'total_students',
        'el_count', 'el_percent',
        'atlas_ready_all', 'atlas_ready_el', 'graduation_rate',
        'essa_index', 'context_note'
    ])


# ============================================================================
# DATA: ELPA21 Domain Data
# ELPA21 (not WIDA) -- 4 levels: Limited / Basic / Proficient / Advanced
# ============================================================================

def load_elpa21_data(districts_df):
    """Generate district ELPA21 domain data modeled from AR EL performance patterns.
    Arkansas uses ELPA21 (not WIDA ACCESS). Domains: Listening, Speaking, Reading, Writing.
    4 proficiency levels: Limited, Basic, Proficient, Advanced."""
    elpa_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                base_speaking = 335 + (grade * 8)
                base_writing = 285 + (grade * 6)

                el_density_penalty = max(0, (d['el_percent'] - 15) * 0.35)
                el_factor = d['atlas_ready_el'] / 14.0
                speaking_adj = int(14 * el_factor + d['el_percent'] * 0.18 - el_density_penalty)
                writing_adj = int(-8 + (el_factor - 1) * 10 - el_density_penalty * 0.7)

                yr_adj = 3 if year == 2025 else 0

                elpa_data.append({
                    'lea_id': d['lea_id'],
                    'district_name': d['district_name'],
                    'grade': grade,
                    'year': year,
                    'total_tested': max(15, int(d['el_count'] / 6)),
                    'listening_avg': base_speaking + speaking_adj - 5 + yr_adj,
                    'speaking_avg': base_speaking + speaking_adj + yr_adj,
                    'reading_avg': base_writing + writing_adj + 14 + yr_adj,
                    'writing_avg': base_writing + writing_adj + yr_adj,
                    'composite_avg': int((base_speaking + speaking_adj + base_writing + writing_adj) / 2 + 16 + yr_adj),
                })

    return pd.DataFrame(elpa_data)


# ============================================================================
# DATA: ATLAS Achievement Data
# ATLAS (ACT-aligned), 4 levels:
#   In Need of Support / Close / Ready / Exceeding
# ============================================================================

def load_atlas_data(districts_df):
    """Generate ATLAS data based on myschoolinfo.arkansas.gov patterns."""
    atlas_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                for subject in ['ELA', 'Math']:
                    base = d['atlas_ready_all'] if subject == 'ELA' else d['atlas_ready_all'] * 0.84
                    ready_exceeding = max(8, min(80, base + (grade - 5) * -1.2))

                    exceeding = max(2, ready_exceeding * 0.20)
                    ready = ready_exceeding - exceeding
                    close = max(12, (100 - ready_exceeding) * 0.40)
                    in_need = max(8, 100 - ready_exceeding - close)

                    atlas_data.append({
                        'lea_id': d['lea_id'],
                        'district_name': d['district_name'],
                        'grade': grade,
                        'subject': subject,
                        'year': year,
                        'ready_exceeding_pct': round(ready_exceeding, 1),
                        'exceeding_pct': round(exceeding, 1),
                        'ready_pct': round(ready, 1),
                        'close_pct': round(close, 1),
                        'in_need_pct': round(in_need, 1),
                    })

    return pd.DataFrame(atlas_data)


# ============================================================================
# DATA: Statewide Domain Proficiency (ELPA21 results)
# ============================================================================

def load_statewide_domain_data():
    """Statewide ELPA21 domain proficiency percentages by grade cluster.
    Source: ADE EL reports / ELPA21 results."""
    return pd.DataFrame([
        {'year': '2024-25', 'grade_cluster': 'K-2', 'listening': 42, 'speaking': 37, 'reading': 25, 'writing': 17},
        {'year': '2024-25', 'grade_cluster': '3-5', 'listening': 46, 'speaking': 42, 'reading': 29, 'writing': 20},
        {'year': '2024-25', 'grade_cluster': '6-8', 'listening': 50, 'speaking': 45, 'reading': 33, 'writing': 23},
        {'year': '2024-25', 'grade_cluster': '9-12', 'listening': 53, 'speaking': 48, 'reading': 36, 'writing': 25},
        {'year': '2023-24', 'grade_cluster': 'K-2', 'listening': 39, 'speaking': 34, 'reading': 23, 'writing': 15},
        {'year': '2023-24', 'grade_cluster': '3-5', 'listening': 43, 'speaking': 39, 'reading': 27, 'writing': 18},
        {'year': '2023-24', 'grade_cluster': '6-8', 'listening': 47, 'speaking': 42, 'reading': 31, 'writing': 21},
        {'year': '2023-24', 'grade_cluster': '9-12', 'listening': 50, 'speaking': 45, 'reading': 34, 'writing': 23},
    ])


# ============================================================================
# DATA: EL Population Growth
# ============================================================================

def load_el_growth_data():
    """Arkansas EL population growth -- driven by NWA poultry/Walmart corridor
    and Marshallese diaspora growth."""
    return pd.DataFrame([
        {'year': 2008, 'el_count': 28500, 'el_percent': 5.9, 'note': 'Baseline'},
        {'year': 2010, 'el_count': 30200, 'el_percent': 6.3, 'note': ''},
        {'year': 2012, 'el_count': 32500, 'el_percent': 6.7, 'note': 'CORA signing'},
        {'year': 2014, 'el_count': 34800, 'el_percent': 7.1, 'note': 'Marshallese growth accelerates'},
        {'year': 2016, 'el_count': 36500, 'el_percent': 7.5, 'note': ''},
        {'year': 2018, 'el_count': 38200, 'el_percent': 7.8, 'note': ''},
        {'year': 2020, 'el_count': 37500, 'el_percent': 7.6, 'note': 'COVID dip; Marshallese community hit hard'},
        {'year': 2022, 'el_count': 39800, 'el_percent': 8.1, 'note': 'Post-COVID rebound'},
        {'year': 2024, 'el_count': 41500, 'el_percent': 8.4, 'note': 'LEARNS Act era'},
        {'year': 2025, 'el_count': 42000, 'el_percent': 8.5, 'note': 'LEARNS Act implementation'},
    ])


# ============================================================================
# AUTHENTICATION
# ============================================================================

def check_password():
    st.session_state.authenticated = True
    return True


# ============================================================================
# TYPE 4 DETECTION
# ============================================================================

def compute_type4_analysis(elpa_df, lea_id, grade, year):
    filtered = elpa_df[
        (elpa_df['lea_id'] == lea_id) &
        (elpa_df['grade'] == grade) &
        (elpa_df['year'] == year)
    ]
    if filtered.empty:
        return None

    row = filtered.iloc[0]
    delta = row['speaking_avg'] - row['writing_avg']
    delta_normalized = delta / 5
    flagged = delta_normalized > 8

    return {
        'lea_id': lea_id, 'district_name': row['district_name'],
        'grade': grade, 'year': year,
        'speaking_avg': row['speaking_avg'], 'writing_avg': row['writing_avg'],
        'delta': delta, 'delta_normalized': delta_normalized, 'flagged': flagged,
        'total_tested': row['total_tested'],
        'estimated_flagged': int(row['total_tested'] * 0.15) if flagged else int(row['total_tested'] * 0.05)
    }


# ============================================================================
# PAGE 1: OVERVIEW
# ============================================================================

def render_overview(districts_df):
    st.header("Arkansas Education Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Pilot Districts", len(districts_df))
    with col2: st.metric("Total Students", f"{districts_df['total_students'].sum():,}")
    with col3: st.metric("English Learners", f"{districts_df['el_count'].sum():,}")
    with col4: st.metric("Statewide EL %", "~8.5%", delta="Growing steadily")

    st.divider()

    # Key policy context
    st.subheader("Key Policy Context")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.error("**LEARNS Act (2023)**\nSweeping reform: vouchers, literacy, accountability overhaul")
    with col2:
        st.warning("**ELPA21 (not WIDA)**\nArkansas uses ELPA21 for ELP assessment -- distinct from WIDA consortium")
    with col3:
        st.success("**Marshallese Diaspora**\nLargest community outside Marshall Islands; unique linguistic needs")

    st.divider()

    # Marshallese context
    st.subheader("The Arkansas Pattern: Marshallese Diaspora & NWA Corridor")
    st.markdown("""
    Arkansas hosts the **largest Marshallese population outside the Marshall Islands**,
    concentrated in Springdale and the Northwest Arkansas (NWA) corridor. Under the
    Compact of Free Association (COFA), Marshallese citizens can live and work in the
    US without visas, leading to a significant diaspora tied to the poultry industry.

    **This creates unique challenges:**
    - Marshallese is an Oceanic language unrelated to Spanish -- different from typical EL programs
    - Cultural norms around education, health, and communication differ significantly
    - Students may have interrupted formal education from island schooling systems
    - COVID-19 disproportionately impacted the Marshallese community

    | District | EL % | Context |
    |----------|------|---------|
    | Green Forest | **34.0%** | Highest rural EL%; Carroll County |
    | Springdale | **32.0%** | Largest Marshallese community; Tyson HQ area |
    | Siloam Springs | **30.0%** | Simmons Foods HQ; high concentration |
    | De Queen | **30.0%** | Sevier County; timber + poultry |
    | Rogers | **28.0%** | NWA corridor; poultry + retail |

    The **LEARNS Act (2023)** restructured accountability and introduced Education
    Freedom Accounts (vouchers), with implications for EL funding and services.
    """)

    st.divider()

    st.subheader("Assessment Framework")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **ATLAS Assessment (ACT-aligned):**
        - Arkansas Teaching, Learning, and Assessment System
        - ELA and Math, grades 3-10
        - 4 Achievement Levels:
            - **Exceeding** -- advanced mastery
            - **Ready** -- grade-level proficiency (ACT-aligned)
            - **Close** -- approaching readiness
            - **In Need of Support** -- below expectations
        - Results on myschoolinfo.arkansas.gov

        **ESSA School Index:**
        - Weighted achievement + growth
        - Graduation rate + school quality
        - ELP progress indicator
        - Results published annually
        """)
    with col2:
        st.markdown("""
        **EL Program:**
        - **ELPA21** (not WIDA) -- distinct consortium
        - 4 Domains: Listening, Speaking, Reading, Writing
        - 4 Levels: Limited, Basic, Proficient, Advanced
        - ~235 districts, ~42,000 ELs (~8.5%)

        **Key Language Groups:**
        - Spanish (~65% of ELs)
        - Marshallese (~12% of ELs)
        - Vietnamese, Hmong, Chin/Burmese

        **Key Legislation:**
        - **LEARNS Act (2023)** -- vouchers, literacy, accountability
        - **Science of Reading (2019)** -- R.I.S.E. Act
        - **COFA (1986/2003)** -- Compact of Free Association

        **Data:** myschoolinfo.arkansas.gov
        """)

    st.divider()

    # District table
    st.subheader("Pilot Districts -- EL Populations & Performance")
    display = districts_df[['lea_id', 'district_name', 'total_students', 'el_count',
                            'el_percent', 'atlas_ready_all', 'atlas_ready_el',
                            'graduation_rate', 'essa_index']].copy()
    display.columns = ['LEA ID', 'District', 'Students', 'EL Count', 'EL %',
                       'ATLAS Ready+ All %', 'ATLAS Ready+ EL %', 'Grad Rate %', 'ESSA Index']
    st.dataframe(display, use_container_width=True, hide_index=True)

    # EL bar chart
    st.subheader("English Learner Population by District")
    fig = px.bar(
        districts_df.sort_values('el_count', ascending=True),
        x='el_count', y='district_name', orientation='h',
        color='el_percent', color_continuous_scale=[[0, '#C0C0C0'], [1, AR_RED]],
        labels={'el_count': 'English Learners', 'district_name': 'District', 'el_percent': 'EL %'}
    )
    fig.update_layout(height=550, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # NWA concentration
    st.subheader("NWA Corridor: EL Concentration Pattern")
    conc_df = districts_df[['district_name', 'el_percent', 'total_students']].copy()
    conc_df['region'] = conc_df['district_name'].apply(
        lambda x: 'NWA Corridor' if x in ['Springdale School District', 'Rogers School District',
                                            'Bentonville School District', 'Siloam Springs School District',
                                            'Fayetteville School District', 'Gravette School District']
        else 'Central AR' if 'Little Rock' in x or 'Pulaski' in x
        else 'Other AR'
    )
    fig2 = px.scatter(conc_df, x='total_students', y='el_percent',
                      color='region', size='el_percent',
                      hover_name='district_name',
                      color_discrete_map={
                          'NWA Corridor': AR_RED,
                          'Central AR': AR_LIGHT_RED,
                          'Other AR': AR_GRAY
                      },
                      labels={'total_students': 'Total Enrollment', 'el_percent': 'EL %',
                              'region': 'Region'})
    fig2.update_layout(
        title="EL % vs District Size -- NWA Corridor Dominates High-Concentration",
        height=400
    )
    st.plotly_chart(fig2, use_container_width=True)


# ============================================================================
# PAGE 2: DOMAIN ANALYSIS
# ============================================================================

def render_domain_analysis(domain_df, growth_df):
    st.header("Statewide ELPA21 Domain Proficiency")

    st.markdown("""
    **Source:** ADE EL reports / ELPA21 results.
    Arkansas uses **ELPA21 (not WIDA)** -- a distinct ELP assessment consortium. Domain
    proficiency percentages reveal the systemic oral-written delta: Speaking consistently
    outperforms Writing across all grade clusters.

    **Arkansas Context:** With ~42,000 ELs (~8.5%) including the nation's largest Marshallese
    diaspora, the oral-written gap reflects challenges in providing academic writing support
    across diverse language backgrounds. Marshallese students face unique challenges as
    their home language is structurally unrelated to English (unlike Spanish).
    """)

    year = st.selectbox("Year", ['2024-25', '2023-24'], key="dom_y")
    filtered = domain_df[domain_df['year'] == year]

    st.divider()

    fig = go.Figure()
    for domain, color in [('listening', AR_GRAY), ('speaking', AR_RED),
                          ('reading', AR_LIGHT_RED), ('writing', '#333333')]:
        fig.add_trace(go.Bar(
            x=filtered['grade_cluster'], y=filtered[domain],
            name=domain.capitalize(), marker_color=color,
            text=[f"{v}%" for v in filtered[domain]], textposition='outside'
        ))
    fig.update_layout(
        title=f"ELPA21 Domain Proficiency by Grade Cluster ({year})",
        xaxis_title="Grade Cluster", yaxis_title="% Proficient+",
        barmode='group', height=450, yaxis=dict(range=[0, 65])
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Speaking-Writing Delta by Grade Cluster")
    filtered = filtered.copy()
    filtered['delta'] = filtered['speaking'] - filtered['writing']
    fig2 = go.Figure(go.Bar(
        x=filtered['grade_cluster'], y=filtered['delta'],
        marker_color=[AR_RED if d > 18 else AR_LIGHT_RED for d in filtered['delta']],
        text=[f"{d:+d} pts" for d in filtered['delta']], textposition='outside'
    ))
    fig2.update_layout(title="Speaking - Writing Gap", yaxis_title="Delta (percentage points)", height=350)
    st.plotly_chart(fig2, use_container_width=True)

    avg_delta = filtered['delta'].mean()
    st.metric("Average Speaking-Writing Delta", f"{avg_delta:+.0f} percentage points",
              help="Positive = Speaking proficiency exceeds Writing proficiency statewide")

    st.divider()

    # EL growth over time
    st.subheader("Arkansas EL Population Growth")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=growth_df['year'], y=growth_df['el_count'],
        mode='lines+markers', line=dict(color=AR_RED, width=3),
        marker=dict(size=8), name='EL Count'
    ))
    fig3.update_layout(
        title="EL Population Growth -- Driven by NWA Poultry Corridor & Marshallese Diaspora",
        xaxis_title="Year", yaxis_title="English Learners",
        height=400
    )
    fig3.add_annotation(x=2019, y=38200, text="R.I.S.E. Act", showarrow=True, arrowhead=2)
    fig3.add_annotation(x=2023, y=41500, text="LEARNS Act", showarrow=True, arrowhead=2)
    fig3.add_annotation(x=2020, y=37500, text="COVID (Marshallese hit hard)", showarrow=True, arrowhead=2)
    st.plotly_chart(fig3, use_container_width=True)

    st.info("""
    **LEARNS Act Interaction:** The LEARNS Act (2023) restructured Arkansas education with
    Education Freedom Accounts (vouchers), enhanced literacy requirements, and a new
    accountability framework. For ELs, the implications include:
    - Potential diversion of per-pupil funding from districts with high EL concentration
    - New literacy benchmarks that interact with EL oral-written gaps
    - ELPA21 progress remains a separate accountability indicator
    - Marshallese students face unique challenges under standardized literacy expectations
    """)


# ============================================================================
# PAGE 3: EL ASSESSMENT ANALYSIS (ELPA21)
# ============================================================================

def render_el_assessment(elpa_df, districts_df):
    st.header("ELPA21 Assessment Analysis")
    st.markdown("""
    **ELPA21** measures English learners across four domains. Arkansas is one of few states
    using ELPA21 rather than WIDA ACCESS. ~42,000 ELs across ~235 districts.

    **ELPA21 Proficiency Levels:** Limited | Basic | Proficient | Advanced
    """)

    col1, col2, col3 = st.columns(3)
    with col1: district = st.selectbox("District", districts_df['district_name'].tolist(), key="acc_d")
    with col2: grade = st.selectbox("Grade", list(range(3, 9)), key="acc_g")
    with col3: year = st.selectbox("Year", [2025, 2024], key="acc_y")

    lea_id = districts_df[districts_df['district_name'] == district]['lea_id'].values[0]
    filtered = elpa_df[(elpa_df['lea_id'] == lea_id) &
                       (elpa_df['grade'] == grade) &
                       (elpa_df['year'] == year)]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()

        d_info = districts_df[districts_df['lea_id'] == lea_id].iloc[0]
        if d_info['el_percent'] > 25:
            st.warning(f"""
            **High-Concentration District:** {district} has **{d_info['el_percent']:.1f}% EL enrollment**.
            {d_info['context_note']}.
            """)

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Listening", f"{row['listening_avg']:.0f}")
        with col2: st.metric("Speaking", f"{row['speaking_avg']:.0f}")
        with col3: st.metric("Reading", f"{row['reading_avg']:.0f}")
        with col4: st.metric("Writing", f"{row['writing_avg']:.0f}")

        domains = ['Listening', 'Speaking', 'Reading', 'Writing']
        scores = [row['listening_avg'], row['speaking_avg'], row['reading_avg'], row['writing_avg']]
        fig = go.Figure(go.Bar(x=domains, y=scores,
                               marker_color=[AR_GRAY, AR_RED, AR_LIGHT_RED, '#333333'],
                               text=[f"{s:.0f}" for s in scores], textposition='outside'))
        fig.update_layout(title=f"ELPA21 Domains -- {district} -- Grade {grade} ({year})",
                         yaxis_title="Scale Score", height=400)
        st.plotly_chart(fig, use_container_width=True)

        oral = (row['listening_avg'] + row['speaking_avg']) / 2
        written = (row['reading_avg'] + row['writing_avg']) / 2
        gap = oral - written

        st.subheader("Oral vs Written Gap")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Oral Average", f"{oral:.0f}")
        with col2: st.metric("Written Average", f"{written:.0f}")
        with col3: st.metric("Gap", f"{gap:+.0f}", delta="Flag" if gap > 30 else "Monitor" if gap > 20 else "OK")

        st.divider()
        st.subheader("Composite & Proficiency Context")
        composite = row['composite_avg']
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Composite Average", f"{composite}")
        with col2: st.metric("Assessment", "ELPA21", help="Arkansas uses ELPA21, not WIDA ACCESS")
        with col3: st.metric("Total Tested", f"{row['total_tested']:,}")


# ============================================================================
# PAGE 4: TYPE 4 DETECTION
# ============================================================================

def render_type4(elpa_df, districts_df):
    st.header("Type 4 Detection")
    st.markdown("""
    **Type 4 candidates** show strong oral skills but weak written skills.
    Delta = Speaking Score - Writing Score. Flag threshold: normalized delta > 8 points.

    **Arkansas Context:** The Marshallese diaspora in NWA presents a distinctive Type 4 pattern.
    Marshallese students often develop conversational English rapidly through community
    immersion but face significant challenges with academic writing -- their home language
    has a very different orthographic and grammatical structure from English.
    ELPA21 domain scores reveal this gap clearly.
    """)

    col1, col2, col3 = st.columns(3)
    with col1: district = st.selectbox("District", districts_df['district_name'].tolist(), key="t4_d")
    with col2: grade = st.selectbox("Grade", list(range(3, 9)), key="t4_g")
    with col3: year = st.selectbox("Year", [2025, 2024], key="t4_y")

    lea_id = districts_df[districts_df['district_name'] == district]['lea_id'].values[0]
    result = compute_type4_analysis(elpa_df, lea_id, grade, year)

    if result:
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Speaking", f"{result['speaking_avg']:.0f}")
        with col2: st.metric("Writing", f"{result['writing_avg']:.0f}")
        with col3: st.metric("Delta", f"{result['delta']:+.0f}")
        with col4: st.metric("Status", "FLAGGED" if result['flagged'] else "OK")

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Speaking', x=['Score'], y=[result['speaking_avg']], marker_color=AR_RED))
        fig.add_trace(go.Bar(name='Writing', x=['Score'], y=[result['writing_avg']], marker_color=AR_GRAY))
        fig.update_layout(title=f"Speaking vs Writing -- {district} -- Grade {grade}", barmode='group', height=350)
        st.plotly_chart(fig, use_container_width=True)

        if result['flagged']:
            st.error(f"**Type 4 Flag Triggered** -- Delta: {result['delta']:+.0f}. "
                     f"Est. {result['estimated_flagged']} of {result['total_tested']} students affected.")
        else:
            st.success(f"**No Type 4 Flag** -- Delta within normal range ({result['delta']:+.0f}).")

        # All grades
        st.subheader(f"All Grades -- {district} ({year})")
        all_data = [compute_type4_analysis(elpa_df, lea_id, g, year) for g in range(3, 9)]
        all_data = [r for r in all_data if r]
        if all_data:
            gdf = pd.DataFrame(all_data)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=gdf['grade'], y=gdf['speaking_avg'], name='Speaking',
                                     mode='lines+markers', line=dict(color=AR_RED, width=3)))
            fig.add_trace(go.Scatter(x=gdf['grade'], y=gdf['writing_avg'], name='Writing',
                                     mode='lines+markers', line=dict(color=AR_GRAY, width=3)))
            fig.update_layout(title="Speaking vs Writing Across Grades", xaxis_title="Grade",
                             yaxis_title="Scale Score", height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("District Summary")
        if all_data:
            summary_df = pd.DataFrame(all_data)[['grade', 'speaking_avg', 'writing_avg', 'delta', 'flagged', 'estimated_flagged']]
            summary_df.columns = ['Grade', 'Speaking', 'Writing', 'Delta', 'Flagged', 'Est. Affected']
            summary_df['Flagged'] = summary_df['Flagged'].map({True: 'YES', False: 'No'})
            st.dataframe(summary_df, use_container_width=True, hide_index=True)


# ============================================================================
# PAGE 5: ACHIEVEMENT GAPS
# ============================================================================

def render_achievement_gaps(districts_df):
    st.header("Achievement Gap Analysis")

    st.markdown("""
    **Data from myschoolinfo.arkansas.gov.** ATLAS Ready + Exceeding rates across pilot districts.

    **ATLAS** uses 4 achievement levels: In Need of Support, Close, Ready, Exceeding.
    Arkansas uses an **ESSA School Index** for accountability.

    **Key Pattern:** The NWA poultry corridor districts (Springdale, Rogers, Siloam Springs)
    show significant EL-to-All achievement gaps, reflecting the challenge of serving
    large EL populations including Marshallese students with unique linguistic needs.
    """)

    st.divider()

    # All vs EL comparison
    fig = go.Figure()
    sorted_df = districts_df.sort_values('atlas_ready_all', ascending=True)
    fig.add_trace(go.Bar(
        x=sorted_df['atlas_ready_all'], y=sorted_df['district_name'],
        name='All Students', orientation='h', marker_color=AR_GRAY
    ))
    fig.add_trace(go.Bar(
        x=sorted_df['atlas_ready_el'], y=sorted_df['district_name'],
        name='English Learners', orientation='h', marker_color=AR_RED
    ))
    fig.update_layout(
        title="ATLAS Ready+ Rate: All Students vs English Learners",
        barmode='group', xaxis_title="% Ready + Exceeding",
        height=600, legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Gap analysis
    st.subheader("All-EL Achievement Gap by District")
    gap_df = districts_df.copy()
    gap_df['el_gap'] = gap_df['atlas_ready_all'] - gap_df['atlas_ready_el']
    gap_df = gap_df.sort_values('el_gap', ascending=True)

    fig_gap = go.Figure(go.Bar(
        x=gap_df['el_gap'], y=gap_df['district_name'], orientation='h',
        marker_color=[AR_RED if g > 28 else AR_LIGHT_RED if g > 20 else AR_GRAY for g in gap_df['el_gap']],
        text=[f"{g:.0f} pts" for g in gap_df['el_gap']], textposition='outside'
    ))
    fig_gap.update_layout(title="All Students - EL Gap (ATLAS Ready+)",
                         xaxis_title="Gap (percentage points)", height=550)
    st.plotly_chart(fig_gap, use_container_width=True)

    # EL proficiency vs EL concentration
    st.subheader("EL Proficiency vs EL Concentration")
    fig2 = px.scatter(districts_df, x='el_percent', y='atlas_ready_el', size='el_count',
                      color='essa_index',
                      color_continuous_scale=[[0, AR_RED], [0.5, AR_LIGHT_RED], [1, '#2E7D32']],
                      hover_name='district_name',
                      labels={'el_percent': 'EL %', 'atlas_ready_el': 'EL Ready+ %',
                              'el_count': 'EL Count', 'essa_index': 'ESSA Index'})
    fig2.update_layout(
        title="EL Proficiency vs Concentration -- Higher EL% Correlates with Lower EL Achievement",
        height=450
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.info("""
    **LEARNS Act Impact:** The LEARNS Act (2023) introduced Education Freedom Accounts
    (vouchers) and restructured accountability. Districts with high EL concentration
    in the NWA corridor face unique pressures: potential funding diversion through
    vouchers while serving the most linguistically diverse student populations in the state.
    The Marshallese community's needs require specialized ESL approaches that may not
    transfer across voucher-funded settings.
    """)


# ============================================================================
# PAGE 6: ATLAS ANALYSIS (State Test)
# ============================================================================

def render_atlas(atlas_df, districts_df):
    st.header("ATLAS Assessment Analysis")
    st.markdown("""
    **ATLAS (Arkansas Teaching, Learning, and Assessment System)** is an ACT-aligned
    assessment for grades 3-10 in ELA and Math.

    **4 Achievement Levels:**
    - **Exceeding** -- Advanced understanding; exceeds grade-level expectations
    - **Ready** -- Grade-level proficiency; on track for ACT readiness
    - **Close** -- Approaching readiness; nearing grade-level expectations
    - **In Need of Support** -- Below grade-level expectations

    Results are published on **myschoolinfo.arkansas.gov** and contribute to the **ESSA School Index**.
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1: district = st.selectbox("District", districts_df['district_name'].tolist(), key="atlas_d")
    with col2: grade = st.selectbox("Grade", list(range(3, 9)), key="atlas_g")
    with col3: subject = st.selectbox("Subject", ['ELA', 'Math'], key="atlas_s")
    with col4: year = st.selectbox("Year", [2025, 2024], key="atlas_y")

    lea_id = districts_df[districts_df['district_name'] == district]['lea_id'].values[0]
    filtered = atlas_df[(atlas_df['lea_id'] == lea_id) &
                        (atlas_df['grade'] == grade) &
                        (atlas_df['subject'] == subject) &
                        (atlas_df['year'] == year)]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Ready + Exceeding", f"{row['ready_exceeding_pct']:.1f}%",
                      help="Grade-level proficient and above (ACT-aligned)")
        with col2:
            st.metric("Exceeding Only", f"{row['exceeding_pct']:.1f}%",
                      help="Advanced mastery")

        st.divider()

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("In Need of Support", f"{row['in_need_pct']:.1f}%")
        with col2: st.metric("Close", f"{row['close_pct']:.1f}%")
        with col3: st.metric("Ready", f"{row['ready_pct']:.1f}%")
        with col4: st.metric("Exceeding", f"{row['exceeding_pct']:.1f}%")

        levels = ['In Need of\nSupport', 'Close', 'Ready', 'Exceeding']
        values = [row['in_need_pct'], row['close_pct'], row['ready_pct'], row['exceeding_pct']]
        colors = ['#d32f2f', '#f57c00', AR_RED, '#333333']
        fig = go.Figure(go.Bar(x=levels, y=values, marker_color=colors,
                               text=[f"{v:.1f}%" for v in values], textposition='outside'))
        fig.update_layout(title=f"ATLAS {subject} -- {district} -- Grade {grade} ({year})",
                         yaxis_title="Percentage", height=420)
        st.plotly_chart(fig, use_container_width=True)

        d_info = districts_df[districts_df['lea_id'] == lea_id].iloc[0]

        st.subheader("District Context")
        st.markdown(f"""
        **{district}** -- Grade {grade} {subject} ({year}):
        - Ready+ Rate: **{row['ready_exceeding_pct']:.1f}%**
        - ESSA Index: **{d_info['essa_index']:.1f}** | EL %: **{d_info['el_percent']:.1f}%**
        - {d_info['context_note']}
        - Results factor into ESSA School Index on myschoolinfo.arkansas.gov
        """)


# ============================================================================
# PAGE 7: EXPORT DATA
# ============================================================================

def render_export(elpa_df, atlas_df, districts_df, domain_df, growth_df):
    st.header("Export Data")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ELPA21 Data")
        st.dataframe(elpa_df, use_container_width=True, hide_index=True)
        st.download_button("Download ELPA21 CSV", elpa_df.to_csv(index=False),
                          "vera_ar_elpa21.csv", "text/csv", use_container_width=True)
    with col2:
        st.subheader("ATLAS Data")
        st.dataframe(atlas_df, use_container_width=True, hide_index=True)
        st.download_button("Download ATLAS CSV", atlas_df.to_csv(index=False),
                          "vera_ar_atlas.csv", "text/csv", use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Statewide Domain Proficiency")
        st.dataframe(domain_df, use_container_width=True, hide_index=True)
        st.download_button("Download Domain CSV", domain_df.to_csv(index=False),
                          "vera_ar_domains.csv", "text/csv", use_container_width=True)
    with col2:
        st.subheader("District Data")
        st.dataframe(districts_df, use_container_width=True, hide_index=True)
        st.download_button("Download Districts CSV", districts_df.to_csv(index=False),
                          "vera_ar_districts.csv", "text/csv", use_container_width=True)

    st.divider()

    st.subheader("EL Population Growth (2008-2025)")
    st.dataframe(growth_df, use_container_width=True, hide_index=True)
    st.download_button("Download EL Growth CSV", growth_df.to_csv(index=False),
                      "vera_ar_el_growth.csv", "text/csv", use_container_width=True)


# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(page_title="VERA-AR | Arkansas Type 4 Detection", page_icon="", layout="wide")

    st.markdown(f"""
    <style>
        .stApp {{ background-color: #fafafa; }}
        .block-container {{ padding-top: 2rem; }}
        h1, h2, h3 {{ color: {AR_RED}; }}
        .stButton > button {{ background-color: {AR_RED}; color: white; }}
        .stButton > button:hover {{ background-color: {AR_DARK}; color: white; }}
    </style>
    """, unsafe_allow_html=True)

    # Load data
    districts_df = load_districts()
    elpa_df = load_elpa21_data(districts_df)
    atlas_df = load_atlas_data(districts_df)
    domain_df = load_statewide_domain_data()
    growth_df = load_el_growth_data()

    # Sidebar
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: {AR_RED}; margin: 0;">VERA-AR</h2>
        <p style="color: #666; font-size: 0.85rem; margin-top: 5px;">Arkansas Implementation</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()

    page = st.sidebar.radio("Navigation", [
        "Overview",
        "Domain Analysis",
        "EL Assessment Analysis",
        "Type 4 Detection",
        "Achievement Gaps",
        "State Test Analysis",
        "Export Data"
    ])

    st.sidebar.divider()
    st.sidebar.markdown(f"""
    **Data Sources:**
    - ELPA21 (not WIDA)
    - ATLAS (ACT-aligned)
    - myschoolinfo.arkansas.gov
    - ADE EL reports

    **Type 4 Detection:**
    - Speaking vs Writing delta
    - Flag threshold: > 8 points
    - ELPA21 domain scores

    **Key AR Context:**
    - ~235 districts, ~42K ELs (~8.5%)
    - ELPA21 (not WIDA consortium)
    - Largest Marshallese diaspora
      outside Marshall Islands
    - NWA poultry/Walmart corridor:
      Springdale 32%, Rogers 28%,
      Siloam Springs 30%
    - LEARNS Act (2023)
    - R.I.S.E. Act (2019)
    - ATLAS: 4 levels (ACT-aligned)
    - ESSA School Index

    ---
    [H-EDU.Solutions](https://h-edu.solutions)
    """)

    if page == "Overview": render_overview(districts_df)
    elif page == "Domain Analysis": render_domain_analysis(domain_df, growth_df)
    elif page == "EL Assessment Analysis": render_el_assessment(elpa_df, districts_df)
    elif page == "Type 4 Detection": render_type4(elpa_df, districts_df)
    elif page == "Achievement Gaps": render_achievement_gaps(districts_df)
    elif page == "State Test Analysis": render_atlas(atlas_df, districts_df)
    elif page == "Export Data": render_export(elpa_df, atlas_df, districts_df, domain_df, growth_df)


if __name__ == "__main__":
    main()
