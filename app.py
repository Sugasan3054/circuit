from flask import Flask, render_template, request, jsonify
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import math

app = Flask(__name__)

class CircuitDiagramGenerator:
    def __init__(self):
        self.components = []
        self.connections = []
        self.grid_size = 50
        self.svg_width = 800
        self.svg_height = 600
        
    def parse_input(self, text):
        """入力テキストを解析して回路情報を抽出"""
        self.components = []
        self.connections = []
        
        # 基本的な回路要素のパターン
        patterns = {
            'resistor': r'(抵抗|レジスタ|R\d*)',
            'capacitor': r'(コンデンサ|キャパシタ|C\d*)',
            'inductor': r'(インダクタ|コイル|L\d*)',
            'battery': r'(電池|バッテリー|電源)',
            'led': r'(LED|発光ダイオード)',
            'switch': r'(スイッチ|SW)',
            'ground': r'(グランド|GND|アース)',
            'voltage_source': r'(電圧源|V\d*)',
            'current_source': r'(電流源|I\d*)'
        }
        
        # 接続を表すパターン
        connection_patterns = [
            r'(\w+)と(\w+)を接続',
            r'(\w+)から(\w+)へ',
            r'(\w+)→(\w+)',
            r'(\w+)-(\w+)',
            r'(\w+)に(\w+)を繋ぐ'
        ]
        
        # 回路要素を検出
        for component_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                component_name = match if isinstance(match, str) else match[0]
                self.components.append({
                    'type': component_type,
                    'name': component_name,
                    'x': 0,
                    'y': 0
                })
        
        # デフォルトの基本回路を追加（何も検出されなかった場合）
        if not self.components:
            self.components = [
                {'type': 'battery', 'name': '電池', 'x': 100, 'y': 200},
                {'type': 'resistor', 'name': '抵抗', 'x': 300, 'y': 200},
                {'type': 'led', 'name': 'LED', 'x': 500, 'y': 200}
            ]
        
        # 接続情報を検出
        for pattern in connection_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                self.connections.append({
                    'from': match[0],
                    'to': match[1]
                })
        
        # 位置を計算
        self._calculate_positions()
        
    def _calculate_positions(self):
        """コンポーネントの位置を計算"""
        if not self.components:
            return
            
        # 簡単なレイアウト: 水平に配置
        spacing = self.svg_width // (len(self.components) + 1)
        
        for i, component in enumerate(self.components):
            component['x'] = spacing * (i + 1)
            component['y'] = self.svg_height // 2
            
    def generate_svg(self):
        """SVG形式の回路図を生成"""
        svg = ET.Element('svg', {
            'width': str(self.svg_width),
            'height': str(self.svg_height),
            'xmlns': 'http://www.w3.org/2000/svg'
        })
        
        # 背景
        ET.SubElement(svg, 'rect', {
            'width': str(self.svg_width),
            'height': str(self.svg_height),
            'fill': 'white',
            'stroke': 'none'
        })
        
        # 接続線を描画
        self._draw_connections(svg)
        
        # コンポーネントを描画
        for component in self.components:
            self._draw_component(svg, component)
            
        return self._prettify_svg(svg)
    
    def _draw_connections(self, svg):
        """接続線を描画"""
        if len(self.components) < 2:
            return
            
        # 簡単な接続: 隣接するコンポーネントを線で結ぶ
        for i in range(len(self.components) - 1):
            comp1 = self.components[i]
            comp2 = self.components[i + 1]
            
            ET.SubElement(svg, 'line', {
                'x1': str(comp1['x'] + 40),
                'y1': str(comp1['y']),
                'x2': str(comp2['x'] - 40),
                'y2': str(comp2['y']),
                'stroke': 'black',
                'stroke-width': '2'
            })
        
        # 最後のコンポーネントから最初のコンポーネントへの接続（回路を閉じる）
        if len(self.components) > 2:
            first = self.components[0]
            last = self.components[-1]
            
            # 下側を通る接続線
            ET.SubElement(svg, 'line', {
                'x1': str(last['x']),
                'y1': str(last['y'] + 20),
                'x2': str(last['x']),
                'y2': str(last['y'] + 80),
                'stroke': 'black',
                'stroke-width': '2'
            })
            
            ET.SubElement(svg, 'line', {
                'x1': str(last['x']),
                'y1': str(last['y'] + 80),
                'x2': str(first['x']),
                'y2': str(first['y'] + 80),
                'stroke': 'black',
                'stroke-width': '2'
            })
            
            ET.SubElement(svg, 'line', {
                'x1': str(first['x']),
                'y1': str(first['y'] + 80),
                'x2': str(first['x']),
                'y2': str(first['y'] + 20),
                'stroke': 'black',
                'stroke-width': '2'
            })
    
    def _draw_component(self, svg, component):
        """個別のコンポーネントを描画"""
        x, y = component['x'], component['y']
        comp_type = component['type']
        
        if comp_type == 'resistor':
            self._draw_resistor(svg, x, y, component['name'])
        elif comp_type == 'capacitor':
            self._draw_capacitor(svg, x, y, component['name'])
        elif comp_type == 'inductor':
            self._draw_inductor(svg, x, y, component['name'])
        elif comp_type == 'battery':
            self._draw_battery(svg, x, y, component['name'])
        elif comp_type == 'led':
            self._draw_led(svg, x, y, component['name'])
        elif comp_type == 'switch':
            self._draw_switch(svg, x, y, component['name'])
        elif comp_type == 'ground':
            self._draw_ground(svg, x, y, component['name'])
        else:
            self._draw_generic(svg, x, y, component['name'])
    
    def _draw_resistor(self, svg, x, y, name):
        """抵抗を描画"""
        # ジグザグ線
        points = []
        for i in range(7):
            px = x - 30 + i * 10
            py = y + (10 if i % 2 == 1 else -10)
            points.append(f"{px},{py}")
        
        ET.SubElement(svg, 'polyline', {
            'points': ' '.join(points),
            'fill': 'none',
            'stroke': 'black',
            'stroke-width': '2'
        })
        
        # 接続線
        ET.SubElement(svg, 'line', {
            'x1': str(x - 40), 'y1': str(y),
            'x2': str(x - 30), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        ET.SubElement(svg, 'line', {
            'x1': str(x + 30), 'y1': str(y),
            'x2': str(x + 40), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        
        # ラベル
        ET.SubElement(svg, 'text', {
            'x': str(x), 'y': str(y - 20),
            'text-anchor': 'middle',
            'font-family': 'Arial',
            'font-size': '12',
            'fill': 'black'
        }).text = name
    
    def _draw_capacitor(self, svg, x, y, name):
        """コンデンサを描画"""
        # 平行線
        ET.SubElement(svg, 'line', {
            'x1': str(x - 5), 'y1': str(y - 20),
            'x2': str(x - 5), 'y2': str(y + 20),
            'stroke': 'black', 'stroke-width': '3'
        })
        ET.SubElement(svg, 'line', {
            'x1': str(x + 5), 'y1': str(y - 20),
            'x2': str(x + 5), 'y2': str(y + 20),
            'stroke': 'black', 'stroke-width': '3'
        })
        
        # 接続線
        ET.SubElement(svg, 'line', {
            'x1': str(x - 40), 'y1': str(y),
            'x2': str(x - 5), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        ET.SubElement(svg, 'line', {
            'x1': str(x + 5), 'y1': str(y),
            'x2': str(x + 40), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        
        # ラベル
        ET.SubElement(svg, 'text', {
            'x': str(x), 'y': str(y - 30),
            'text-anchor': 'middle',
            'font-family': 'Arial',
            'font-size': '12',
            'fill': 'black'
        }).text = name
    
    def _draw_inductor(self, svg, x, y, name):
        """インダクタを描画（コイル）"""
        # 半円を複数描画してコイルを表現
        for i in range(4):
            cx = x - 15 + i * 10
            ET.SubElement(svg, 'path', {
                'd': f'M {cx} {y} A 5 5 0 0 1 {cx + 10} {y}',
                'fill': 'none',
                'stroke': 'black',
                'stroke-width': '2'
            })
        
        # 接続線
        ET.SubElement(svg, 'line', {
            'x1': str(x - 40), 'y1': str(y),
            'x2': str(x - 15), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        ET.SubElement(svg, 'line', {
            'x1': str(x + 15), 'y1': str(y),
            'x2': str(x + 40), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        
        # ラベル
        ET.SubElement(svg, 'text', {
            'x': str(x), 'y': str(y - 20),
            'text-anchor': 'middle',
            'font-family': 'Arial',
            'font-size': '12',
            'fill': 'black'
        }).text = name
    
    def _draw_battery(self, svg, x, y, name):
        """電池を描画"""
        # 長い線（正極）
        ET.SubElement(svg, 'line', {
            'x1': str(x + 5), 'y1': str(y - 20),
            'x2': str(x + 5), 'y2': str(y + 20),
            'stroke': 'black', 'stroke-width': '3'
        })
        # 短い線（負極）
        ET.SubElement(svg, 'line', {
            'x1': str(x - 5), 'y1': str(y - 10),
            'x2': str(x - 5), 'y2': str(y + 10),
            'stroke': 'black', 'stroke-width': '3'
        })
        
        # 接続線
        ET.SubElement(svg, 'line', {
            'x1': str(x - 40), 'y1': str(y),
            'x2': str(x - 5), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        ET.SubElement(svg, 'line', {
            'x1': str(x + 5), 'y1': str(y),
            'x2': str(x + 40), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        
        # +/- 記号
        ET.SubElement(svg, 'text', {
            'x': str(x + 15), 'y': str(y + 5),
            'text-anchor': 'middle',
            'font-family': 'Arial',
            'font-size': '14',
            'fill': 'red'
        }).text = '+'
        
        ET.SubElement(svg, 'text', {
            'x': str(x - 15), 'y': str(y + 5),
            'text-anchor': 'middle',
            'font-family': 'Arial',
            'font-size': '14',
            'fill': 'blue'
        }).text = '-'
        
        # ラベル
        ET.SubElement(svg, 'text', {
            'x': str(x), 'y': str(y - 30),
            'text-anchor': 'middle',
            'font-family': 'Arial',
            'font-size': '12',
            'fill': 'black'
        }).text = name
    
    def _draw_led(self, svg, x, y, name):
        """LEDを描画"""
        # 三角形
        ET.SubElement(svg, 'polygon', {
            'points': f'{x-15},{y-10} {x-15},{y+10} {x+5},{y}',
            'fill': 'none',
            'stroke': 'black',
            'stroke-width': '2'
        })
        
        # 縦線
        ET.SubElement(svg, 'line', {
            'x1': str(x + 5), 'y1': str(y - 10),
            'x2': str(x + 5), 'y2': str(y + 10),
            'stroke': 'black', 'stroke-width': '2'
        })
        
        # 接続線
        ET.SubElement(svg, 'line', {
            'x1': str(x - 40), 'y1': str(y),
            'x2': str(x - 15), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        ET.SubElement(svg, 'line', {
            'x1': str(x + 5), 'y1': str(y),
            'x2': str(x + 40), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        
        # 光の矢印
        ET.SubElement(svg, 'path', {
            'd': f'M {x+10} {y-15} L {x+15} {y-20} M {x+12} {y-20} L {x+15} {y-20} L {x+15} {y-17}',
            'fill': 'none',
            'stroke': 'orange',
            'stroke-width': '1'
        })
        
        # ラベル
        ET.SubElement(svg, 'text', {
            'x': str(x), 'y': str(y - 30),
            'text-anchor': 'middle',
            'font-family': 'Arial',
            'font-size': '12',
            'fill': 'black'
        }).text = name
    
    def _draw_switch(self, svg, x, y, name):
        """スイッチを描画"""
        # 接点
        ET.SubElement(svg, 'circle', {
            'cx': str(x - 15), 'cy': str(y),
            'r': '2', 'fill': 'black'
        })
        ET.SubElement(svg, 'circle', {
            'cx': str(x + 15), 'cy': str(y),
            'r': '2', 'fill': 'black'
        })
        
        # スイッチ線
        ET.SubElement(svg, 'line', {
            'x1': str(x - 15), 'y1': str(y),
            'x2': str(x + 10), 'y2': str(y - 10),
            'stroke': 'black', 'stroke-width': '2'
        })
        
        # 接続線
        ET.SubElement(svg, 'line', {
            'x1': str(x - 40), 'y1': str(y),
            'x2': str(x - 15), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        ET.SubElement(svg, 'line', {
            'x1': str(x + 15), 'y1': str(y),
            'x2': str(x + 40), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        
        # ラベル
        ET.SubElement(svg, 'text', {
            'x': str(x), 'y': str(y - 25),
            'text-anchor': 'middle',
            'font-family': 'Arial',
            'font-size': '12',
            'fill': 'black'
        }).text = name
    
    def _draw_ground(self, svg, x, y, name):
        """グランドを描画"""
        # 縦線
        ET.SubElement(svg, 'line', {
            'x1': str(x), 'y1': str(y),
            'x2': str(x), 'y2': str(y + 20),
            'stroke': 'black', 'stroke-width': '2'
        })
        
        # 横線（3本）
        for i, length in enumerate([20, 12, 6]):
            ET.SubElement(svg, 'line', {
                'x1': str(x - length//2), 'y1': str(y + 20 + i * 4),
                'x2': str(x + length//2), 'y2': str(y + 20 + i * 4),
                'stroke': 'black', 'stroke-width': '2'
            })
        
        # 接続線
        ET.SubElement(svg, 'line', {
            'x1': str(x - 40), 'y1': str(y),
            'x2': str(x), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        
        # ラベル
        ET.SubElement(svg, 'text', {
            'x': str(x), 'y': str(y - 10),
            'text-anchor': 'middle',
            'font-family': 'Arial',
            'font-size': '12',
            'fill': 'black'
        }).text = name
    
    def _draw_generic(self, svg, x, y, name):
        """汎用コンポーネントを描画"""
        # 四角形
        ET.SubElement(svg, 'rect', {
            'x': str(x - 20), 'y': str(y - 15),
            'width': '40', 'height': '30',
            'fill': 'lightgray',
            'stroke': 'black',
            'stroke-width': '2'
        })
        
        # 接続線
        ET.SubElement(svg, 'line', {
            'x1': str(x - 40), 'y1': str(y),
            'x2': str(x - 20), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        ET.SubElement(svg, 'line', {
            'x1': str(x + 20), 'y1': str(y),
            'x2': str(x + 40), 'y2': str(y),
            'stroke': 'black', 'stroke-width': '2'
        })
        
        # ラベル
        ET.SubElement(svg, 'text', {
            'x': str(x), 'y': str(y + 5),
            'text-anchor': 'middle',
            'font-family': 'Arial',
            'font-size': '10',
            'fill': 'black'
        }).text = name
    
    def _prettify_svg(self, elem):
        """SVGを整形"""
        rough_string = ET.tostring(elem, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

# Flask アプリケーション
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_circuit():
    data = request.get_json()
    description = data.get('description', '')
    
    generator = CircuitDiagramGenerator()
    generator.parse_input(description)
    svg_content = generator.generate_svg()
    
    return jsonify({'svg': svg_content})

# HTMLテンプレート
html_template = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>回路図生成アプリ</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .input-section {
            margin-bottom: 30px;
        }
        label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            color: #555;
        }
        textarea {
            width: 100%;
            height: 120px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            resize: vertical;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .output-section {
            margin-top: 30px;
        }
        .circuit-display {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 20px;
            background-color: #fafafa;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .examples {
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .examples h3 {
            margin-top: 0;
            color: #495057;
        }
        .examples ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        .examples li {
            margin: 5px 0;
        }
        .loading {
            color: #666;
            font-style: italic;
        }
        .error {
            color: #dc3545;
            background-color: #f8d7da;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔌 回路図生成アプリ</h1>
        
        <div class="input-section">
            <label for="description">回路の説明を入力してください:</label>
            <textarea id="description" placeholder="例: 電池と抵抗とLEDを直列に接続した回路"></textarea>
            
            <button onclick="generateCircuit()">回路図を生成</button>
            
            <div class="examples">
                <h3>入力例:</h3>
                <ul>
                    <li>電池と抵抗とLEDを直列に接続</li>
                    <li>電源、抵抗、コンデンサの基本回路</li>
                    <li>LEDとスイッチと電池の回路</li>
                    <li>抵抗とコンデンサの並列回路</li>
                    <li>インダクタと抵抗を含む回路</li>
                </ul>
            </div>
        </div>
        
        <div class="output-section">
            <h2>生成された回路図:</h2>
            <div id="circuit-display" class="circuit-display">
                <p>上記のテキストボックスに回路の説明を入力して、「回路図を生成」ボタンを押してください。</p>
            </div>
        </div>
    </div>

    <script>
        async function generateCircuit() {
            const description = document.getElementById('description').value;
            const displayDiv = document.getElementById('circuit-display');
            const button = document.querySelector('button');
            
            if (!description.trim()) {
                displayDiv.innerHTML = '<p class="error">回路の説明を入力してください。</p>';
                return;
            }
            
            // ローディング状態
            button.disabled = true;
            displayDiv.innerHTML = '<p class="loading">回路図を生成中...</p>';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ description: description })
                });
                
                if (!response.ok) {
                    throw new Error('サーバーエラーが発生しました');
                }
                
                const data = await response.json();
                displayDiv.innerHTML = data.svg;
                
            } catch (error) {
                displayDiv.innerHTML = `<p class="error">エラーが発生しました: ${error.message}</p>`;
            } finally {
                button.disabled = false;
            }
        }
        
        // Enterキーでも生成できるように
        document.getElementById('description').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                generateCircuit();
            }
        });
    </script>
</body>
</html>
'''

# templatesディレクトリが存在しない場合のために、動的にテンプレートを返す
@app.route('/templates/<path:filename>')
def templates(filename):
    if filename == 'index.html':
        return html_template
    return "Template not found", 404

# テンプレートを直接返すためのルート
@app.route('/')
def index():
    return html_template

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)