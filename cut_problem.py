import streamlit as st
from collections import defaultdict
import io

# =========================
# FUNCIÓN PRINCIPAL
# =========================
def allocate_bars(piece_lengths, piece_counts, BAR_LENGTH, scale=100):
    capacity = int(round(BAR_LENGTH * scale))
    items = []

    for length, count in zip(piece_lengths, piece_counts):
        length_i = int(round(length * scale))
        items += [length_i] * count

    # Mejora simple: ordenar descendente
    items.sort(reverse=True)

    bars = []
    total_waste = 0.0

    while items:
        dp = [False] * (capacity + 1)
        dp[0] = True
        prev_w = [-1] * (capacity + 1)
        prev_idx = [-1] * (capacity + 1)

        for idx, p in enumerate(items):
            for w in range(capacity, p - 1, -1):
                if dp[w - p] and not dp[w]:
                    dp[w] = True
                    prev_w[w] = w - p
                    prev_idx[w] = idx

        w_max = max(w for w in range(capacity + 1) if dp[w])

        used_idx = []
        w = w_max
        while w > 0:
            idx = prev_idx[w]
            used_idx.append(idx)
            w = prev_w[w]

        bar_count = defaultdict(int)
        for idx in sorted(used_idx, reverse=True):
            length_i = items.pop(idx)
            bar_count[length_i] += 1

        waste = (capacity - w_max) / scale
        total_waste += waste

        bars.append({
            'counts': {l / scale: c for l, c in bar_count.items()},
            'waste': waste
        })

    return len(bars), bars, total_waste


# =========================
# FORMATO DE INSTRUCCIONES
# =========================
def format_instructions_grouped(bars):
    patterns = {}

    for bar in bars:
        counts_tuple = tuple(sorted(bar['counts'].items()))
        waste = round(bar['waste'], 2)
        key = (counts_tuple, waste)
        patterns[key] = patterns.get(key, 0) + 1

    lines = []
    for (counts_tuple, waste), num in patterns.items():
        lines.append(f"{num} barra(s) con:")
        for length, cnt in counts_tuple:
            lines.append(f"  - {cnt} pieza(s) de {length:.2f} m")
        lines.append(f"  Desperdicio por barra: {waste:.2f} m")
        lines.append("")

    return "\n".join(lines)


# =========================
# STREAMLIT APP
# =========================
st.set_page_config(page_title="Optimización de Corte de Barras", layout="centered")

st.title("🔩 Optimización de Corte de Barras")
st.write("Asignación de piezas a barras minimizando desperdicio.")

# -------- INPUTS --------
st.subheader("📥 Datos de entrada")

bar_length = st.number_input(
    "Longitud de la barra (m)",
    min_value=1.0,
    value=12.0,
    step=0.1
)

st.write("Ingrese las piezas (una por fila):")

num_rows = st.number_input(
    "Cantidad de tipos de piezas",
    min_value=1,
    value=4,
    step=1
)

piece_lengths = []
piece_counts = []

for i in range(int(num_rows)):
    col1, col2 = st.columns(2)
    with col1:
        length = st.number_input(
            f"Longitud pieza #{i+1} (m)",
            min_value=0.01,
            value=1.0,
            key=f"len_{i}"
        )
    with col2:
        count = st.number_input(
            f"Cantidad pieza #{i+1}",
            min_value=1,
            value=10,
            step=1,
            key=f"cnt_{i}"
        )

    piece_lengths.append(length)
    piece_counts.append(count)

# -------- EJECUCIÓN --------
st.divider()

if st.button("🚀 Calcular optimización"):
    with st.spinner("Calculando asignación óptima..."):
        bars_used, bars, total_waste = allocate_bars(
            piece_lengths,
            piece_counts,
            bar_length
        )

        instructions = format_instructions_grouped(bars)

    # -------- RESULTADOS --------
    st.subheader("📊 Resultados")

    st.success(
        f"Se emplean **{bars_used} barras** de {bar_length} m\n\n"
        f"🔻 **Desperdicio total:** {total_waste:.2f} m"
    )

    st.subheader("📄 Instrucciones de corte")
    st.text(instructions)

    # -------- DESCARGA --------
    st.subheader("⬇️ Descargar resultados")

    file_buffer = io.StringIO()
    file_buffer.write(instructions)

    st.download_button(
        label="📥 Descargar instrucciones (.txt)",
        data=file_buffer.getvalue(),
        file_name="instrucciones_corte.txt",
        mime="text/plain"
    )
