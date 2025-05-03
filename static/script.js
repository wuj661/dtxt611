//addEventListener 是一个方法，用于为某个 DOM 元素绑定事件监听器,"DOMContentLoaded" 是一个浏览器内置的事件，表示 HTML 文档的 DOM 树已经完全加载和解析完成
document.addEventListener("DOMContentLoaded", function() {

    //click：触发时机：用户点击某个元素时触发。用途：处理按钮点击、链接点击等交互行为。
    //load：触发时机：当整个页面（包括所有资源，如图片、样式表等）加载完成后触发。 用途：确保所有资源都加载完成后再执行某些操作
    //DOMContentLoaded： 触发时机：当 HTML 文档的 DOM 树完全加载和解析完成时触发。 用途：用于操作 DOM 元素，但不等待外部资源（如图片、CSS）加载完成

    //.sidebar button 表示“在 .sidebar 容器内的所有 <button> 元素”,buttons 是一个常量变量，使用 const 声明 class ="sidebar"即是sidebar容器
    const buttons = document.querySelectorAll('.sidebar button');
    // 为每个侧边栏按钮添加点击事件监听器
    buttons.forEach(button => {
        //当前按钮（button）绑定一个点击事件监听器。当用户点击该按钮时，触发匿名函数 function() { ... } 中定义的操作
        button.addEventListener('click', function() {
            // 移除所有按钮的激活状态
            buttons.forEach(btn => btn.classList.remove('active'));
            // 添加当前点击按钮的激活状态
            this.classList.add('active');

            // 隐藏所有内容区域
            hideAllSections();
            // 根据点击的按钮显示相应的内容区域 ，通过id判断点击的是那个按钮
            if (this.id === 'categoryBtn') {
                //给默认的界面隐藏
                hideSections('defaultMessage');
                showSection('dynamicContent'); //showSection为一个在下面写的函数，document.getElementById(dynamicContent).style.display = 'block'
                showCategoryColumn();//上面的是第一层容器，即点击题目分类后的所有内容，在点击后有两个容器，对这两个容器进行定义
            } else if (this.id === 'addQuestionBtn') {
                hideSections('defaultMessage');
                showSection('addQuestionForm');//是一个录题的界面
            } else if (this.id === 'challengeRecordBtn') {
                hideSections('defaultMessage');
                showSection('challengeRecordContent');//展示index里面的challengeRecordContent，那里是用来展示界面的
                loadChallengeRecords();//点击挑战记录加载挑战记录函数
            } else if (this.id === 'wrongRecordBtn') {
                hideSections('defaultMessage');
                showSection('wrongRecordContent');
                loadWrongRecords();
            } else if (this.id === 'analysisBtn') {
                hideSections('defaultMessage');
                showSection('analysisContent');
            }
        });
    });

    // 隐藏除默认的所有内容区域函数
    function hideAllSections() {
        document.getElementById('dynamicContent').style.display = 'none';
        document.getElementById('addQuestionForm').style.display = 'none';
        document.getElementById('challengeRecordContent').style.display = 'none';
        document.getElementById('wrongRecordContent').style.display = 'none';
        document.getElementById('analysisContent').style.display = 'none';
    }
    // 隐藏单个内容区域函数
    function hideSections(sectionId) {
        document.getElementById(sectionId).style.display = 'none';
    }
    // 显示指定内容区域函数
    function showSection(sectionId) {
        document.getElementById(sectionId).style.display = 'block';
    }

    // 显示题目分类列函数
    function showCategoryColumn() {
        document.getElementById('categoryColumn').style.display = 'block';
        document.getElementById('difficultyColumn').style.display = 'none';
    }
    // 显示难度等级列函数，修改这里，让点击分类后，分类和难度都展示
    function showDifficultyColumn() {
        document.getElementById('categoryColumn').style.display = 'block';
        document.getElementById('difficultyColumn').style.display = 'block';
    }


    const categoryButtons = document.querySelectorAll(".category-btn");
    // 为每个题目分类按钮添加点击事件监听器
    categoryButtons.forEach(button => {
        button.addEventListener("click", function () {
            const categoryColor = this.style.backgroundColor; // 获取按钮背景颜色
            showDifficultyColumn(); // 显示难度等级列

            const difficultyButtons = document.querySelectorAll(".difficulty-btn");
            // 设置所有难度按钮的颜色与题目分类按钮相同
            difficultyButtons.forEach(difficultyBtn => {
                difficultyBtn.style.backgroundColor = categoryColor;
            });

            const category = this.getAttribute("data-category"); // 获取题目分类
            document.getElementById('difficultyTitle').innerText = `${category} - 难度等级`; // 更新难度等级标题

            // 为每个难度按钮添加点击事件监听器
            difficultyButtons.forEach(difficultyBtn => {
                difficultyBtn.addEventListener("click", function () {
                    const difficulty = this.getAttribute("data-difficulty"); // 获取难度等级
                    window.location.href = `/quiz/${category}/${difficulty}`; // 跳转到对应的Quiz页面
                });
            });
        });
    });

    const form = document.getElementById('questionForm');
    if (form) {
        // 为表单添加提交事件监听器
        form.addEventListener('submit', function (event) {
            event.preventDefault(); // 阻止默认的表单提交行为

            // 使用Fetch API发送POST请求
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form)
            })
            .then(response => response.json()) // 将响应转换为JSON格式
            .then(data => {
                const messageDiv = document.getElementById('message');
                messageDiv.innerHTML = `<div style="color: green;">${data.message}</div>`; // 显示成功消息
                form.reset(); // 重置表单
            })
            .catch(error => {
                console.error('Error:', error); // 输出错误信息
            });
        });
    }

    // 加载挑战记录函数 只加载空表格
    function loadChallengeRecords() {
        fetch('/get_challenge_records') // 发送GET请求获取挑战记录，app.py需要有对应路由返回数据
            .then(response => response.json()) // 将响应转换为JSON格式
            .then(data => {  //.then(data => { ... }) 处理解析后的 JSON 数据
            //使用 CSS 选择器查找 ID 为 challengeTable 的表格中的 <tbody> 元素
                const challengeTableBody = document.querySelector('#challengeTable tbody');
                challengeTableBody.innerHTML = ''; // 清空表格内容 innerHTML 是一个属性，用于获取或设置某个元素的 HTML 内容

                //data 是从服务器获取的 JSON 数据，其中 records 是一个数组，app.py中有，包含多条记录
                data.records.forEach((record, index) => {    //forEach 是 JavaScript 数组的一个方法，用于遍历数组中的每个元素。 (record, index)：record 是当前遍历到的记录对象，index 是该记录在数组中的索引（从 0 开始）
                    const row = document.createElement('tr'); // 创建表格行 <tr> 是 HTML 中的表格行标签，用于存放表格数据单元格（<td> 或 <th>）

                    const serialNumberCell = document.createElement('td'); // 序号单元格
                    serialNumberCell.textContent = index + 1;
                    row.appendChild(serialNumberCell);

                    const userIdCell = document.createElement('td'); // 用户ID单元格
                    userIdCell.textContent = record.user_id;
                    row.appendChild(userIdCell);

                    const categoryCell = document.createElement('td'); // 题目分类单元格
                    categoryCell.textContent = record.category;
                    row.appendChild(categoryCell);

                    const difficultyCell = document.createElement('td'); // 难度等级单元格
                    difficultyCell.textContent = record.difficulty;
                    row.appendChild(difficultyCell);

                    const scoreCell = document.createElement('td'); // 挑战分数单元格
                    scoreCell.textContent = record.score.toFixed(2);
                    row.appendChild(scoreCell);

                    const submitTimeCell = document.createElement('td'); // 挑战时间单元格
                    submitTimeCell.textContent = new Date(record.submit_time).toLocaleString();
                    row.appendChild(submitTimeCell);

                    challengeTableBody.appendChild(row); // 将行添加到表格中
                });
            })
            .catch(error => {
                console.error('Error loading challenge records:', error); // 输出错误信息
            });
    }



    // 加载错题记录函数
    function loadWrongRecords() {
        fetch('/get_wrong_records') // 发送GET请求，app.py需要有对应路由返回数据
            .then(response => response.json()) // 将响应转换为JSON格式
            .then(data => {
                const wrongTableBody = document.querySelector('#wrongTable tbody');
                wrongTableBody.innerHTML = ''; // 清空表格内容

                const errorCounts = {}; // 统计每个用户对每个问题的错误次数
                data.records.forEach(record => {
                    const key = `${record.user_id}-${record.question_id}`;
                    if (!errorCounts[key]) {
                        errorCounts[key] = {
                            user_id: record.user_id,
                            question_id: record.question_id,
                            count: 0
                        };
                    }
                    errorCounts[key].count += 1;
                });

                const sortedRecords = Object.values(errorCounts).sort((a, b) => b.count - a.count); // 按错误次数排序

                sortedRecords.forEach(record => {
                    const row = document.createElement('tr'); // 创建表格行

                    const userIdCell = document.createElement('td'); // 用户ID单元格
                    userIdCell.textContent = record.user_id;
                    row.appendChild(userIdCell);

                    const questionIdCell = document.createElement('td'); // 题目ID单元格
                    const questionLink = document.createElement('a'); // 题目链接
                    questionLink.className = 'question-link';
                    questionLink.textContent = record.question_id;
                    questionLink.setAttribute('href', `/question/${record.question_id}`);
                    questionLink.setAttribute('target', '_self'); // 在同一标签页打开链接
                    questionIdCell.appendChild(questionLink);
                    row.appendChild(questionIdCell);

                    const errorCountCell = document.createElement('td'); // 错误次数单元格
                    errorCountCell.textContent = record.count;
                    row.appendChild(errorCountCell);

                    wrongTableBody.appendChild(row); // 将行添加到表格中
                });
            })
            .catch(error => {
                console.error('Error loading wrong records:', error); // 输出错误信息
            });
    }

    // 题目中遇到这些字符就换行展示
    const specialChars = [':', '①', '⑥', '⑤', '③', '②', '④'];
    document.querySelectorAll('.question-text').forEach(questionText => {
        let innerHTML = questionText.innerHTML;
        specialChars.forEach(char => {
            innerHTML = innerHTML.split(char).join('<br>' + char);
        });
        questionText.innerHTML = innerHTML;
    });


    hideAllSections(); // 初始化时隐藏所有内容区域
});



