import speedtest
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import datetime

def run_speedtest():
    st = speedtest.Speedtest()
    st.download()
    st.upload()
    res = st.results.dict()
    return {
        'timestamp': datetime.datetime.now(),
        'download': res['download'] / 1e6,
        'upload': res['upload'] / 1e6,
        'ping': res['ping']
    }

app = dash.Dash(__name__)

df = pd.DataFrame(columns=['timestamp', 'download', 'upload', 'ping'])

app.layout = html.Div([
    html.H1("Internet Speed Test Dashboard"),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,
        n_intervals=0
    ),
    dcc.Graph(id='live-update-graph'),
    html.Div(id='speedtest-results')
])

@app.callback(Output('live-update-graph', 'figure'),
              Output('speedtest-results', 'children'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    global df
    result = run_speedtest()
    result_df = pd.DataFrame([result])
    df = pd.concat([df, result_df], ignore_index=True)

    fig = px.line(df, x='timestamp', y=['download', 'upload', 'ping'],
                  labels={'value': 'Speed (Mbps) / Ping (ms)', 'timestamp': 'Timestamp'},
                  title='Internet Speed Over Time')
    fig.update_layout(transition_duration=500)

    latest_result = f"Latest Result: Download: {result['download']:.2f} Mbps, Upload: {result['upload']:.2f} Mbps, Ping: {result['ping']:.2f} ms"
    return fig, latest_result

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

