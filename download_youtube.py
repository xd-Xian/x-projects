import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from pytube import YouTube

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def serve_layout():
    return html.Div([
        dbc.Row('Copy Youtube Link to Here:*'),
        dbc.Row(dbc.Input(id='link', placeholder='YouTube Link', type='url', bs_size='sm', debounce=True)),
        dbc.Row('Save Video to:*'),
        dbc.Row(dbc.Input(id='path', placeholder='Folder', type='text', bs_size='sm', debounce=True)),
        dbc.Row([
            dbc.Col(dbc.Button('Download', id='download', size='sm', n_clicks=0, style={'width': '100%'}), width=1, style={'padding-left': '0px'}),
            dbc.Col(dbc.Button('Clear', id='clear', size='sm', n_clicks=0, style={'width': '100%'}), width=1),
        ], style={'margin-top': '10px'}),
        dbc.Spinner(dbc.Row(id='output'))
    ], style={'margin': '10%'})

app.layout = serve_layout


@app.callback(
    [Output('link', 'value'), Output('path', 'value')],
    [Input('clear', 'n_clicks')],
    [State('link', 'value'), State('path', 'value')]
)
def clear_input(clear, link, path):
    if link is None or path is None:
        raise dash.exceptions.PreventUpdate

    ctx = dash.callback_context
    button_id = ''
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    print (button_id)
    if clear>0 and button_id=='clear':
        return None, None
    else:
        return dash.no_update, dash.no_update


@app.callback(
    Output('output', 'children'),
    [Input('download', 'n_clicks')],
    [State('link', 'value'), State('path', 'value')]
)
def get_link(n_clicks, link, path):
    if n_clicks==0 or link is None or path is None:
        raise dash.exceptions.PreventUpdate

    try:
        yt = YouTube(link) 
    except: 
        #print ("Connection Error") #to handle exception 
        return html.Div('Connection Error !', style={'color': 'red'})
    
    stream = yt.streams.first()
    try: 
        # downloading the video 
        stream.download(path)
        return html.Div('Download Successful !')
    except: 
        return html.Div('Download Error !', style={'color': 'red'})


if __name__=="__main__":
    app.run_server(debug=True)
