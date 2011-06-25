#ifndef METAWINDOW_HPP
#define MEATWINDOW_HPP
#include <QMainWindow>
#include <QTableView>
//#include <QFileSystemWatcher>
#include <phonon/audiooutput.h>
#include <phonon/seekslider.h>
#include <phonon/mediaobject.h>
#include <phonon/volumeslider.h>
#include <phonon/audiooutput.h>
#include <QSqlTableModel>
#include "MusicLibrary.hpp"

class QTabWidget;
class QPushButton;
class QAction;

namespace UDJ{


class SettingsWidget;

class MetaWindow : public QMainWindow{
  Q_OBJECT
public:
  MetaWindow();
private slots:
  void stateChanged(Phonon::State newState, Phonon::State oldState);
  void tick(qint64 time);
  void sourceChanged(const Phonon::MediaSource &source);
  void setMusicDir();
  void tableClicked(const QModelIndex& index);
  
private:
  QTabWidget *tabs;
  Phonon::SeekSlider *seekSlider;
  Phonon::MediaObject *mediaObject;
  Phonon::AudioOutput *audioOutput;
  Phonon::VolumeSlider *volumeSlider;
  QTableView* libraryView;
  QTableView* playlistView;
  QTableView* partiersView;
  QSqlTableModel* libraryModel;
  SettingsWidget* settingsWidget;

  QAction *playAction;
  QAction *pauseAction;
  QAction *stopAction;
  QAction *setMusicDirAction;
  QAction *quitAction;

  MusicLibrary library;

//  QFileSystemWatcher* fileWatcher;

  void createActions();
  void setupUi();
  void setupMenus();
  static QModelIndex getFilePathIndex(const QModelIndex& songIndex);
};


} //end namespace 
#endif //METAWINDOW_HPP