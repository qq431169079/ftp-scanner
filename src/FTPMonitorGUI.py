# Built ins
import threading

# wxpython
import wxversion
wxversion.select( "3.0" )
import wx

# Project modules
import FTPCrawler
from AddFTPSourceDialog import AddFTPSourceDialog
from SuperListCtrl import SuperListCtrl
import ftp_service_comm
import ftp_download_service

ADD_SOURCE_TOOL_ID = wx.NewId()
SCAN_SOURCES_TOOL_ID = wx.NewId()
DOWNLOAD_TOOL_ID = wx.NewId()
STOP_SCAN_TOOL_ID = wx.NewId()


class FTPMonitorGUI(wx.Frame):

    def __init__(self):
        frame_style = wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX
        super(FTPMonitorGUI, self).__init__(None, style=frame_style)

        self.sources_listctrl = None
        self.scan_button = None
        self.results_listctrl = None
        self.progress_bar = None
        self.log_textctrl = None
        self.quit_request = False

        self.init_ui()

        self.destinations = [ ]
        local = ftp_download_service.DownloadService( )
        local.start( )
        self.destinations.append( local )
        remote = ftp_service_comm.Client( '127.0.0.1', 1066 )
        self.destinations.append( remote )

        self.sources_listctrl.add_row(['67.172.255.177', '/Public/Movies/Z'])
        #self.sources_listctrl.add_row(['24.162.163.232', '/shares/STAR/movies'])

    def init_ui(self):
        self.Title = 'FTP Monitor'
        self.SetBackgroundColour(wx.Colour(240, 240, 240))
        icon_bundle = wx.IconBundle()
        icon_bundle.AddIconFromFile(r'resources/cheeseburger.ico', wx.BITMAP_TYPE_ANY)
        self.SetIcons(icon_bundle)

        # Setup Toolbar
        toolbar = self.CreateToolBar()
        add_source_image = wx.Image(r'resources/add_32.png').ConvertToBitmap()
        scan_source_image = wx.Image(r'resources/scan_32.png').ConvertToBitmap()
        download_image = wx.Image(r'resources/download_32.png').ConvertToBitmap()
        stop_image = wx.Image(r'resources/stop.png').ConvertToBitmap()
        toolbar.AddTool(ADD_SOURCE_TOOL_ID, bitmap=add_source_image)
        toolbar.AddTool(SCAN_SOURCES_TOOL_ID, bitmap=scan_source_image)
        toolbar.AddTool(DOWNLOAD_TOOL_ID, bitmap=download_image)
        toolbar.AddTool(STOP_SCAN_TOOL_ID, bitmap=stop_image)
        toolbar.Realize()
        self.Bind(event=wx.EVT_TOOL, id=ADD_SOURCE_TOOL_ID, handler=self.add_source_button_callback)
        self.Bind(event=wx.EVT_TOOL, id=SCAN_SOURCES_TOOL_ID, handler=self.scan_sources_button_callback)
        self.Bind(event=wx.EVT_TOOL, id=DOWNLOAD_TOOL_ID, handler=self.download_button_callback)
        self.Bind(event=wx.EVT_TOOL, id=STOP_SCAN_TOOL_ID, handler=self.stop_scan_button_callback)

        splitter = wx.SplitterWindow(parent=self)

        sources_panel = wx.Panel(parent=splitter)
        sources_label = wx.StaticText(parent=sources_panel, label='Sources')
        self.sources_listctrl = SuperListCtrl(parent=sources_panel, columns=['IP', 'Search Path'])
        sources_panel_vsizer = wx.BoxSizer(wx.VERTICAL)
        sources_panel_vsizer.Add(item=sources_label)
        sources_panel_vsizer.Add(item=self.sources_listctrl, flag=wx.EXPAND, proportion=1)
        sources_panel.SetSizer(sources_panel_vsizer)

        results_panel = wx.Panel(parent=splitter)
        results_label = wx.StaticText(parent=results_panel, label='Results')
        results_columns = ['Title', 'Episode Title', 'Episode Number', 'Season', 'Rating', 'Genre', 'Duration', 'IMDB Rating', 'Resolution', 'Year', 'File Size', 'IP', 'Filename']
        self.results_listctrl = SuperListCtrl(parent=results_panel, columns=results_columns)
        results_panel_vsizer = wx.BoxSizer(wx.VERTICAL)
        results_panel_vsizer.Add(results_label)
        results_panel_vsizer.Add(self.results_listctrl, flag=wx.EXPAND, proportion=1)
        results_panel.SetSizer(results_panel_vsizer)

        splitter.SplitVertically(sources_panel, results_panel)
        splitter.SetMinimumPaneSize(300)

        self.progress_bar = wx.Gauge(parent=self)


        splitter2 = wx.SplitterWindow(parent=self)
        log_panel = wx.Panel(parent=splitter2)
        log_label = wx.StaticText(parent=log_panel, label='Log')
        self.log_textctrl = wx.TextCtrl(parent=log_panel, style=wx.TE_READONLY | wx.TE_MULTILINE)
        log_panel_vsizer = wx.BoxSizer(wx.VERTICAL)
        log_panel_vsizer.Add( log_label )
        log_panel_vsizer.Add( self.log_textctrl, flag=wx.EXPAND, proportion=1 )
        log_panel.SetSizer( log_panel_vsizer )

        downloads_panel = wx.Panel(parent=splitter2)
        downloads_label = wx.StaticText(parent=downloads_panel, label='Downloads')
        self.downloads_listctrl = SuperListCtrl(parent=downloads_panel, columns=[ 'Status', 'Source', 'Dest', 'Speed' ])
        downloads_panel_vsizer = wx.BoxSizer(wx.VERTICAL)
        downloads_panel_vsizer.Add( downloads_label )
        downloads_panel_vsizer.Add( self.downloads_listctrl, flag=wx.EXPAND, proportion=1 )
        downloads_panel.SetSizer( downloads_panel_vsizer )

        splitter2.SplitVertically( log_panel, downloads_panel )
        splitter2.SetMinimumPaneSize(300)



        main_vsizer = wx.BoxSizer(wx.VERTICAL)
        main_vsizer.Add(splitter, flag=wx.EXPAND | wx.ALL, proportion=4, border=5)
        main_vsizer.Add(self.progress_bar, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
        main_vsizer.Add(splitter2, flag=wx.EXPAND | wx.ALL, proportion=1, border=5)
        #main_vsizer.Add(self.log_textctrl, flag=wx.EXPAND | wx.ALL, proportion=1, border=5)

        self.SetSizer(main_vsizer)

        self.Show()
        self.SetSize((800, 500))

    def process_new_result(self, result_dict):
        row_data = []
        row_data.append(result_dict.get('name','-'))
        row_data.append(result_dict.get('episode_title','-'))
        row_data.append(result_dict.get('episode','-'))
        row_data.append(result_dict.get('season','-'))
        row_data.append(result_dict.get('rating', '-'))
        genre_list = result_dict.get('imdb_rating','-')
        if genre_list != '-':
            genre_list = ', '.join([genre for genre in genre_list])
        row_data.append(genre_list)
        row_data.append(result_dict.get('duration', '-'))
        row_data.append(result_dict.get('imdb_rating','-'))
        row_data.append(result_dict.get('screen_size','-'))
        row_data.append(result_dict.get('year','-'))
        row_data.append(result_dict.get('filesize','-'))
        row_data.append(result_dict.get('ip','-'))
        row_data.append(result_dict.get('filename','-'))

        print '\tRAW:',result_dict
        print '\tNEW ROW:',row_data


        keys = ['title', 'episode_title', 'episode', 'season', 'screen_size', 'year', 'filesize', 'ip', 'filename']
        #row_data = [str(result_dict.get(key, '-')) for key in keys]

        self.log(row_data)

        self.results_listctrl.add_row(row_data)

    def log(self, message):
        self.log_textctrl.AppendText(str(message)+'\n')

    def stop_scan_button_callback(self, event):
        event.Skip()
        self.quit_request = True

    def add_source_button_callback(self, event):
        event.Skip()

        add_source_dialog = AddFTPSourceDialog(self)
        add_source_dialog.ShowModal()

        if add_source_dialog.canceled:
            pass
        else:
            self.sources_listctrl.add_row([add_source_dialog.ip, add_source_dialog.path])

    def scanner_worker(self, sources):
        for source in sources:
            self.log('Scanning {} -> {}'.format(source['IP'], source['Search Path']))
            crawler = FTPCrawler.FTPCrawler(source['IP'], source['Search Path'], self)
            crawler.connect()
            crawler.scan()

    def scan_sources_button_callback(self, event):
        if event:
            event.Skip()
        sources = self.sources_listctrl.get_all_rows()
        scanning_thread = threading.Thread(target=self.scanner_worker, args=(sources,))
        scanning_thread.start()

    def download_button_callback(self, event):
        event.Skip()
        rows = self.results_listctrl.get_all_rows( )
        selected = self.results_listctrl.GetNextSelected( -1 )
        print 'download'
        print rows[ selected ]


def main():
    app = wx.App()
    FTPMonitorGUI()
    app.MainLoop()


if __name__ == '__main__':
    main()