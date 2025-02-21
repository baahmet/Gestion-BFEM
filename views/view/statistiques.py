import sys
import sqlite3
from typing import Dict, Tuple, Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QHBoxLayout, QPushButton, QFrame, QMessageBox, QComboBox
)
from PyQt5.QtGui import QFont, QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QRectF, QMargins
from PyQt5.QtChart import (
    QChart, QChartView, QPieSeries, QBarSeries, QBarSet, 
    QBarCategoryAxis, QValueAxis, QPieSlice
)



STATUS_COLORS = {
    "Admis": QColor("#2ECC71"),      # Vert
    "2nd Tour": QColor("#F1C40F"),   # Jaune
    "Échec": QColor("#E74C3C"),      # Rouge
    "Repêchage": QColor("#3498DB")   # Bleu
}

class ChartView(QChartView):
    """Widget personnalisé pour les graphiques."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(400)  # Augmentation de la hauteur
        self.setMinimumWidth(500)   # Définition d'une largeur minimale


# Constants
STYLES = {
    "PRIMARY_COLOR": "#2C3E50",
    "ACCENT_COLOR": "#1ABC9C",
    "TEXT_COLOR": "#FFFFFF",
    "HOVER_COLOR": "#2980B9",
    "ERROR_COLOR": "#E74C3C",
    "SUCCESS_COLOR": "#2ECC71"
}

class StatCard(QFrame):
    """Widget personnalisé pour afficher une statistique avec un titre et une valeur."""
    def __init__(self, title: str, value: int, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet(f"""
            StatCard {{
                background-color: rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Roboto", 12))
        title_label.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Roboto", 16, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)

STATUS_COLORS = {
    "Admis": QColor("#2ECC71"),      # Vert
    "2nd Tour": QColor("#F1C40F"),   # Jaune
    "Échec": QColor("#E74C3C"),      # Rouge
    "Repêchage": QColor("#3498DB")   # Bleu
}

class ChartView(QChartView):
    """Widget personnalisé pour les graphiques."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(400)  # Augmentation de la hauteur
        self.setMinimumWidth(500)   # Définition d'une largeur minimale


class Statistiques(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Statistiques des Délibérations")
        self.setGeometry(200, 100, 1000, 800)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {STYLES['PRIMARY_COLOR']};
                color: {STYLES['TEXT_COLOR']};
                font-family: 'Roboto';
            }}
            QPushButton {{
                background-color: {STYLES['ACCENT_COLOR']};
                border: none;
                padding: 10px;
                border-radius: 5px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {STYLES['HOVER_COLOR']};
            }}
            QComboBox {{
                background-color: {STYLES['ACCENT_COLOR']};
                border: none;
                padding: 5px;
                border-radius: 5px;
                min-width: 150px;
            }}
        """)

        self.conn = None
        self.cur = None
        self.init_database()
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        # En-tête
        self.setup_header()
        
        # Contenu
        self.setup_content()
        
        # Charger les données initiales
        self.charger_statistiques()

    def init_database(self):
        """Initialise la connexion à la base de données avec gestion d'erreurs."""
        try:
            self.conn = sqlite3.connect("bfem_db.sqlite")
            self.cur = self.conn.cursor()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur Base de données", 
                               f"Impossible de se connecter à la base de données: {str(e)}")
            sys.exit(1)

    def setup_header(self):
        """Configure l'en-tête de l'application."""
        header_layout = QHBoxLayout()
        
        # Titre
        self.title = QLabel("Statistiques Globales")
        self.title.setFont(QFont("Roboto", 24, QFont.Bold))
        self.title.setAlignment(Qt.AlignLeft)
        
        # Sélecteur d'année
        self.year_selector = QComboBox()
        self.year_selector.addItems(["Toutes les années", "2024", "2023", "2022"])
        self.year_selector.currentTextChanged.connect(self.charger_statistiques)
        
        # Bouton de rafraîchissement
        self.refresh_btn = QPushButton("Rafraîchir")
        self.refresh_btn.clicked.connect(self.charger_statistiques)
        
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        header_layout.addWidget(self.year_selector)
        header_layout.addWidget(self.refresh_btn)
        
        self.layout.addLayout(header_layout)

  

    def get_statistics(self) -> Optional[Dict[str, dict]]:
        """Récupère les statistiques détaillées de la base de données."""
        try:
            # Récupérer d'abord le total des candidats
            self.cur.execute("""
                SELECT COUNT(*) 
                FROM Candidats
            """)
            total_candidats = self.cur.fetchone()[0]

            # Récupérer les statistiques par statut
            self.cur.execute("""
                SELECT 
                    D.statut,
                    COUNT(*) as nombre,
                    ROUND(CAST(COUNT(*) AS FLOAT) * 100 / CAST((
                        SELECT COUNT(*) 
                        FROM Deliberation
                    ) AS FLOAT), 2) as pourcentage
                FROM Deliberation D
                GROUP BY D.statut
                ORDER BY nombre DESC
            """)
            
            resultats = self.cur.fetchall()
            
            # Initialiser les statistiques avec tous les statuts possibles
            stats = {
                "Total Candidats": total_candidats,
                "Admis": {"nombre": 0, "pourcentage": 0.0},
                "2nd Tour": {"nombre": 0, "pourcentage": 0.0},
                "Échec": {"nombre": 0, "pourcentage": 0.0},
                "Repêchage": {"nombre": 0, "pourcentage": 0.0}
            }
            
            # Mettre à jour les statistiques avec les données récupérées
            for statut, nombre, pourcentage in resultats:
                if statut in stats:
                    stats[statut] = {
                        "nombre": nombre,
                        "pourcentage": pourcentage
                    }
            
            return stats

        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la récupération des statistiques: {str(e)}")
            return None

    def charger_statistiques(self):
        """Met à jour l'interface avec les dernières statistiques."""
        # Nettoyer les widgets existants
        for i in reversed(range(self.stats_layout.count())): 
            widget = self.stats_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Charger les nouvelles statistiques
        stats = self.get_statistics()
        if not stats:
            return

        print("Données récupérées :", stats)  # Ajoutez ce log pour vérifier les données

        # Créer les cartes de statistiques
        total_card = StatCard("Total Candidats", stats["Total Candidats"])
        self.stats_layout.addWidget(total_card)

        for statut, data in stats.items():
            if statut != "Total Candidats":
                stat_text = f"{data['nombre']} ({data['pourcentage']}%)"
                stat_card = StatCard(statut, stat_text)
                self.stats_layout.addWidget(stat_card)

        # Mettre à jour les graphiques
        self.update_charts(stats)
        

    def update_charts(self, stats: Dict[str, dict]):
        """Met à jour les graphiques avec les nouvelles données."""
        print("Données reçues pour les graphiques :", stats)  # Ajoutez ce log pour vérifier les données

        # Graphique circulaire
        pie_series = QPieSeries()
        
        # Ajouter les tranches avec leurs couleurs respectives
        for statut, data in stats.items():
            if statut != "Total Candidats":
                print(f"Statut : {statut}, Données : {data}")  # Ajoutez ce log pour vérifier chaque statut
                slice = QPieSlice(
                    statut,
                    float(data['nombre'])
                )
                pie_series.append(slice)
                
                # Définir la couleur de la tranche
                if statut in STATUS_COLORS:
                    slice.setBrush(STATUS_COLORS[statut])
                
                # Configurer l'étiquette
                slice.setLabelVisible(True)
                slice.setLabelPosition(QPieSlice.LabelOutside)
                label_text = f"{statut}\n{data['nombre']} ({data['pourcentage']}%)"
                slice.setLabel(label_text)
                
                # Ajouter des effets au survol
                slice.setExploded(True)
                slice.setExplodeDistanceFactor(0.1)

        pie_chart = QChart()
        pie_chart.addSeries(pie_series)
        pie_chart.setTitle("Répartition des Résultats")
        pie_chart.setTitleFont(QFont("Roboto", 12, QFont.Bold))
        pie_chart.setAnimationOptions(QChart.SeriesAnimations)
        pie_chart.legend().setVisible(True)
        pie_chart.legend().setAlignment(Qt.AlignRight)
        
        # Ajuster les marges pour les étiquettes
        pie_chart.setMargins(QMargins(10, 10, 10, 10))
        
        # Ajuster la taille des tranches
        pie_series.setPieSize(0.7)  # 70% de la taille disponible
        
        self.pie_chart.setChart(pie_chart)
        
        # Graphique en barres
        bar_set = QBarSet("Nombre de candidats")
        categories = []
        
        for statut, data in stats.items():
            if statut != "Total Candidats":
                categories.append(statut)
                bar_set.append(data['nombre'])
                
                # Définir la couleur de la barre
                if statut in STATUS_COLORS:
                    bar_set.setColor(STATUS_COLORS[statut])

        bar_series = QBarSeries()
        bar_series.append(bar_set)

        bar_chart = QChart()
        bar_chart.addSeries(bar_series)
        bar_chart.setTitle("Comparaison des Résultats")
        bar_chart.setTitleFont(QFont("Roboto", 12, QFont.Bold))
        bar_chart.setAnimationOptions(QChart.SeriesAnimations)

        # Axes
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        bar_chart.addAxis(axis_x, Qt.AlignBottom)
        bar_series.attachAxis(axis_x)

        axis_y = QValueAxis()
        max_value = max(data['nombre'] for statut, data in stats.items() if statut != "Total Candidats")
        axis_y.setRange(0, max_value * 1.1)
        axis_y.setTitleText("Nombre de candidats")
        bar_chart.addAxis(axis_y, Qt.AlignLeft)
        bar_series.attachAxis(axis_y)

        self.bar_chart.setChart(bar_chart)
    def setup_content(self):
        """Configure le contenu principal de l'application."""
        # Layout pour les cartes de statistiques
        self.stats_layout = QHBoxLayout()
        self.layout.addLayout(self.stats_layout)
        
        # Layout pour les graphiques avec espacement
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)  # Ajouter de l'espacement entre les graphiques
        
        # Créer un conteneur pour chaque graphique
        pie_container = QFrame()
        pie_container.setFrameStyle(QFrame.StyledPanel)
        pie_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        pie_layout = QVBoxLayout(pie_container)
        self.pie_chart = ChartView()
        pie_layout.addWidget(self.pie_chart)
        
        bar_container = QFrame()
        bar_container.setFrameStyle(QFrame.StyledPanel)
        bar_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        bar_layout = QVBoxLayout(bar_container)
        self.bar_chart = ChartView()
        bar_layout.addWidget(self.bar_chart)
        
        # Ajouter les conteneurs au layout des graphiques
        charts_layout.addWidget(pie_container)
        charts_layout.addWidget(bar_container)
        
        self.layout.addLayout(charts_layout)


    def closeEvent(self, event):
        """Gère la fermeture propre de l'application."""
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error:
                pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Statistiques()
    window.show()
    sys.exit(app.exec_())