# --- GRÁFICOS Y MÉTRICAS ---
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric("Inversión Inicial (CAPEX)", f"{fmt(total_capex)} €")
with m_col2:
    st.metric("Total Ayudas Captadas", f"{fmt(total_ayudas)} €")
with m_col3:
    exposicion = total_capex - total_fondo_perdido
    st.metric("Exposición Neta Socios", f"{fmt(exposicion)} €", delta=f"{fmt(exposicion - 20000)} € vs Capital", delta_color="inverse")
with m_col4:
    st.metric("Coste Operativo Anual (OPEX)", f"{fmt(total_opex_anual)} €")

fig_roi = go.Figure()
fig_roi.add_trace(go.Scatter(x=anios, y=lista_flujo_acum, mode='lines+markers', name='Flujo Acumulado', line=dict(color='#2ca02c', width=4)))
fig_roi.add_trace(go.Scatter(x=anios, y=[0]*5, mode='lines', name='Equilibrio', line=dict(color='red', dash='dash')))
fig_roi.update_layout(title="Curva de Retorno (Incluyendo Financiación Externa)", template="plotly_white", yaxis_title="Euros (€)")
# FIX: Cambio por width='stretch'
st.plotly_chart(fig_roi, width='stretch')

# --- SIMULACIÓN 1-50 DRONES ---
st.subheader("📊 Gráfico de Escalabilidad (1 a 50 Drones)")
r_drones = list(range(1, 51))
curva_total = []
for n in r_drones:
    c_capex = (13500 * n * (1-dcto_volumen)) + (3500 * n) + (sw_base + (500*(n-1) if n>1 else 0)) + (sora_base + (1000*(n-1) if n>1 else 0)) + (3000 * n)
    c_opex = (1200 + 1200*n) + (360*n) + (600 + (350*(n-1) if n>1 else 0)) + (2000*n) + (2500 if n<=3 else 4500)
    curva_total.append(c_capex + c_opex)

fig_esc = go.Figure()
fig_esc.add_trace(go.Scatter(x=r_drones, y=curva_total, mode='lines', name='Inversión Total Año 1', line=dict(color='#9467bd', width=3)))
fig_esc.update_layout(xaxis_title="Número de Drones", yaxis_title="Gasto Total Año 1 (€)", template="plotly_white")
# FIX: Cambio por width='stretch'
st.plotly_chart(fig_esc, width='stretch')