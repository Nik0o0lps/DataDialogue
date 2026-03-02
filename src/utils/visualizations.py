"""
Utilitários para criar visualizações de dados.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Any


class DataVisualizer:
    """Cria visualizações apropriadas para diferentes tipos de dados."""
    
    @staticmethod
    def auto_visualize(df: pd.DataFrame, query: str = "") -> Optional[go.Figure]:
        """
        Cria automaticamente a melhor visualização para os dados.
        
        Args:
            df: DataFrame com os dados
            query: Query original (opcional, para contexto)
            
        Returns:
            Figura Plotly ou None se não for possível visualizar
        """
        if df.empty:
            return None
        
        # Detectar tipo de visualização baseado na estrutura dos dados
        num_cols = len(df.columns)
        num_rows = len(df)
        
        # Se for muito grande, mostrar apenas tabela
        if num_rows > 100 or num_cols > 10:
            return None
        
        # Identificar colunas numéricas e categóricas
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Filtrar colunas ID das numéricas (não devem ser visualizadas)
        numeric_cols = [col for col in numeric_cols if 'id' not in col.lower()]
        
        # Caso 1: Uma coluna categórica e uma numérica = Gráfico de barras
        if len(categorical_cols) == 1 and len(numeric_cols) == 1:
            return DataVisualizer.create_bar_chart(df, categorical_cols[0], numeric_cols[0])
        
        # Caso 2: Dados temporais = Gráfico de linha
        if DataVisualizer._has_temporal_data(df):
            return DataVisualizer.create_line_chart(df)
        
        # Caso 3: Múltiplas categorias com valores = Gráfico de barras agrupadas
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            return DataVisualizer.create_bar_chart(df, categorical_cols[0], numeric_cols[0])
        
        # Caso 4: Apenas valores numéricos em uma coluna = gráfico de pizza (se fizer sentido)
        if num_cols == 2 and len(categorical_cols) == 1 and len(numeric_cols) == 1:
            if num_rows <= 10:  # Pizzas funcionam bem com poucos segmentos
                return DataVisualizer.create_pie_chart(df, categorical_cols[0], numeric_cols[0])
        
        return None
    
    @staticmethod
    def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, 
                        title: str = "Gráfico de Barras") -> go.Figure:
        """Cria um gráfico de barras (horizontal se apropriado)."""
        
        # Decidir se deve ser horizontal
        # Usar horizontal se: muitas categorias, nomes longos, ou nome de pessoas
        num_categories = len(df[x_col].unique())
        max_label_length = df[x_col].astype(str).str.len().max()
        use_horizontal = num_categories > 5 or max_label_length > 15 or 'nome' in x_col.lower()
        
        # Para gráfico horizontal: inverter x e y
        # Horizontal = categorias no eixo Y (vertical), valores no eixo X (horizontal)
        if use_horizontal:
            fig = px.bar(
                df, 
                x=y_col,  # Valores vão para o eixo horizontal (X)
                y=x_col,  # Categorias vão para o eixo vertical (Y)
                orientation='h',
                title=title,
                labels={x_col: x_col.replace('_', ' ').title(), 
                       y_col: y_col.replace('_', ' ').title()},
                color=y_col,
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(
                height=max(400, num_categories * 40),  # Altura dinâmica
                showlegend=False
            )
        else:
            fig = px.bar(
                df, 
                x=x_col,  # Categorias no eixo horizontal (X)
                y=y_col,  # Valores no eixo vertical (Y)
                title=title,
                labels={x_col: x_col.replace('_', ' ').title(), 
                       y_col: y_col.replace('_', ' ').title()},
                color=y_col,
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(
                xaxis_tickangle=-45,
                height=500,
                showlegend=False
            )
        
        return fig
    
    @staticmethod
    def create_line_chart(df: pd.DataFrame, title: str = "Tendência ao Longo do Tempo") -> go.Figure:
        """Cria um gráfico de linha para dados temporais."""
        # Identificar coluna de data
        date_col = None
        for col in df.columns:
            if 'data' in col.lower() or 'date' in col.lower():
                date_col = col
                break
        
        if not date_col:
            # Usar primeira coluna como eixo X
            date_col = df.columns[0]
        
        # Identificar colunas numéricas
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        fig = go.Figure()
        
        for col in numeric_cols:
            fig.add_trace(go.Scatter(
                x=df[date_col],
                y=df[col],
                mode='lines+markers',
                name=col.replace('_', ' ').title(),
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=date_col.replace('_', ' ').title(),
            yaxis_title='Valor',
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def create_pie_chart(df: pd.DataFrame, labels_col: str, values_col: str,
                        title: str = "Distribuição") -> go.Figure:
        """Cria um gráfico de pizza."""
        fig = px.pie(
            df,
            names=labels_col,
            values=values_col,
            title=title,
            hole=0.3  # Fazer um donut chart
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=500)
        
        return fig
    
    @staticmethod
    def _has_temporal_data(df: pd.DataFrame) -> bool:
        """Verifica se o DataFrame contém dados temporais."""
        for col in df.columns:
            if 'data' in col.lower() or 'date' in col.lower():
                return True
        return False
    
    @staticmethod
    def create_comparison_chart(df: pd.DataFrame, title: str = "Comparação") -> go.Figure:
        """Cria um gráfico de comparação entre categorias."""
        if len(df.columns) < 2:
            return None
        
        x_col = df.columns[0]
        
        fig = go.Figure()
        
        for col in df.columns[1:]:
            if pd.api.types.is_numeric_dtype(df[col]):
                fig.add_trace(go.Bar(
                    name=col.replace('_', ' ').title(),
                    x=df[x_col],
                    y=df[col]
                ))
        
        fig.update_layout(
            title=title,
            barmode='group',
            xaxis_tickangle=-45,
            height=500
        )
        
        return fig
