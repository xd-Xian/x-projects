import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH
from pytube import YouTube

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def serve_layout():
    return html.Div([
        dbc.Row(
            dbc.Col(dbc.Button('+', id='add_task', n_clicks=0, style={'width': '100%'}), width=1, style={'padding-left': '0px'}),
        ),
        dbc.Modal(id='modal', children=[
            #dbc.ModalHeader('YouTube Link'),
            dbc.ModalBody([
                html.Div('Copy Youtube Link to Here:*'),
                dbc.Input(id='link', placeholder='YouTube Link', type='url', bs_size='sm'),#, debounce=True
                html.Div('Save Video to:*'),
                dbc.Input(id='path', placeholder='Folder', type='text', bs_size='sm'),#, debounce=True
            ]),
            dbc.ModalFooter([
                dbc.Button('Confirm', id='confirm'),
                dbc.Button('Clear', id='clear'),
                dbc.Button('Cancel', id='cancel')
            ])
        ]),
        dbc.Row(
            dbc.Col([], id='content', style={'border-top': '1px solid lightgray', 'border-left': '1px solid lightgray', 'border-right': '1px solid lightgray'}),
            style={'margin-top': '10px'}
        ),

        dcc.ConfirmDialog(
            id='dupe_confirm',
            message="Item is already in your task! Are you sure you want to download again?",  
        ),

        #dcc.ConfirmDialog(
        #    id='final_confirm',
        #    message="Start downloading",  
        #),

        dcc.Store(id='links', data=[]),
        dcc.Store(id='paths', data=[]),
        dcc.Store(id='dupe_flag', data=0)
    ], style={'margin': '5% 20%'})

app.layout = serve_layout


@app.callback(
    Output('modal', 'is_open'), 
    [Input('add_task', 'n_clicks'), Input('confirm', 'n_clicks'), Input('cancel', 'n_clicks')],
    [State('modal', 'is_open')]
)
def toggle_modal(add_task, confirm, cancel, is_open):
    if add_task or confirm or cancel:
        return not is_open
    return is_open


@app.callback(
    Output('confirm', 'disabled'),
    [Input('link', 'value'), Input('path', 'value')]
)
def valid_confirm(link, path):
    if link and path:
        return False
    else:
        return True


@app.callback(
    [Output('link', 'value'), Output('path', 'value')],
    [Input('clear', 'n_clicks'), Input('cancel', 'n_clicks')]
)
def clear_input(clear, cancel):
    if not clear and not cancel:
        raise dash.exceptions.PreventUpdate
    return None, None


@app.callback(
    [Output('dupe_confirm', 'displayed'), Output('dupe_flag', 'data')],
    [Input('confirm', 'n_clicks')], 
    [State('link', 'value'), State('path', 'value'), State('links', 'data'), State('paths', 'data')]
)
def dupe_confirm(confirm, link, path, links, paths):
    if not confirm or not link or not path:
        raise dash.exceptions.PreventUpdate
    for i in range(len(links)):
        if link==links[i] and path==paths[i]:
            return True, 1
    return False, 0



@app.callback(
    [Output('links', 'data'), Output('paths', 'data')],
    [Input('confirm', 'n_clicks'), Input('dupe_confirm', 'submit_n_clicks'), Input('dupe_confirm', 'cancel_n_clicks')], 
    [State('link', 'value'), State('path', 'value'), State('links', 'data'), State('paths', 'data'), State('dupe_flag', 'data')]
)
def confirm_task(confirm, dupe_confirm, dupe_cancel, link, path, links, paths, dupe_flag):
    if not confirm or not link or not path:
        raise dash.exceptions.PreventUpdate

    ctx = dash.callback_context
    button_id = ''
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id']
    if (dupe_flag==0 and button_id=='confirm.n_clicks') or (dupe_flag==1 and button_id=='dupe_confirm.submit_n_clicks'):
        links.append(link)
        paths.append(path)
        return links, paths
    else:
        #return dash.no_update, dash.no_update
        raise dash.exceptions.PreventUpdate


@app.callback(
    Output('content', 'children'),
    [Input('links', 'data'), Input('paths', 'data')], 
    [State('content', 'children')]
)
def main(links, paths, content):
    if not links or not paths:
        raise dash.exceptions.PreventUpdate
    try: 
        yt = YouTube(links[-1]) 
        title = yt.title
        status = dbc.Spinner(html.Div(id={'type': 'status', 'index': len(links)-1}))
    except: 
        title = None
        status = html.Div("Connection Error!", style={'color': 'red'})

    if len(links)==1:
        content.append(
            dbc.Row([
                dbc.Col('Title', width=4, style={'font-weight': 'bold'}),
                dbc.Col('Path', width=4, style={'font-weight': 'bold'}),
                dbc.Col('Status', width=4, style={'font-weight': 'bold'}),
            ])
        )
    content.append(
        dbc.Row([
            dbc.Col(title, width=4),
            dbc.Col(paths[-1], width=4),
            dbc.Col(status, width=4),
            dcc.Store(data=links[-1], id={'type': 'link', 'index': len(links)-1}),
            dcc.Store(data=paths[-1], id={'type': 'path', 'index': len(links)-1})
        ])
    )
    return content



@app.callback(
    Output({'type': 'status', 'index': MATCH}, 'children'),
    [Input({'type': 'link', 'index': MATCH}, 'data'), Input({'type': 'path', 'index': MATCH}, 'data')],
    [State({'type': 'status', 'index': MATCH}, 'children')]
)
def downloading(link, path, status):
    if status:
        raise dash.exceptions.PreventUpdate
    yt = YouTube(link) 
    stream = yt.streams.first()
    try:  
        stream.download(path)
        status = "Download Successful!"
    except: 
        status = html.Div("Some Error!", style={'color': 'red'})
    return status


if __name__=="__main__":
    app.run_server(debug=True)
