(() => {
    'use strict';
    const search = document.querySelector('[data-section-search]');
    const statusFilter = document.querySelector('[data-section-status]');
    const sectionRows = Array.from(document.querySelectorAll('[data-section-row]'));
    const resultCount = document.querySelector('[data-section-filter-count]');
    const noResults = document.querySelector('[data-filter-empty]');
    function filterSections() {
        const query = (search?.value || '').trim().toLocaleLowerCase();
        const status = statusFilter?.value || 'all';
        let visible = 0;
        sectionRows.forEach(row => {
            const matchesText = `${row.dataset.title || ''} ${row.dataset.slug || ''}`.toLocaleLowerCase().includes(query);
            const matchesStatus = status === 'all' || row.dataset.status === status;
            const show = matchesText && matchesStatus;
            row.hidden = !show;
            if (show) visible++;
        });
        if (resultCount) resultCount.textContent = `عرض ${visible} من ${sectionRows.length} أقسام`;
        if (noResults) noResults.hidden = visible !== 0;
    }
    search?.addEventListener('input', filterSections);
    statusFilter?.addEventListener('change', filterSections);
    const form = document.querySelector('[data-section-form]');
    if (!form) return;
    const stack = form.querySelector('[data-block-stack]');
    const workspace = form.querySelector('.composer-workspace');
    const hidden = form.querySelector('#blocks-json');
    const initial = document.querySelector('#initial-blocks');
    const preview = form.querySelector('[data-preview]');
    const count = form.querySelector('[data-block-count]');
    const status = form.querySelector('.save-state');
    const statusLabel = form.querySelector('[data-save-label]');
    const composer = form.querySelector('[data-composer]');
    const mode = form.elements.content_mode;
    const names = {heading:'عنوان',paragraph:'فقرة',list:'قائمة',steps:'خطوات',callout:'تنبيه أو معلومة',image:'صورة',table:'جدول',code:'كتلة برمجية',mermaid:'مخطط Mermaid',link:'رابط',divider:'فاصل'};
    const marks = {heading:'H',paragraph:'¶',list:'☷',steps:'↗',callout:'✦',image:'▧',table:'▦',code:'</>',mermaid:'◇',link:'↗',divider:'—'};
    const allowed = Object.keys(names);
    const allowedWidths = ['full','wide','half','third'];
    const allowedAlignments = ['start','center','end'];
    const esc = value => String(value ?? '');
    const lines = value => Array.isArray(value) ? value.join('\n') : esc(value);
    const blocks = (() => {
        try { const parsed = JSON.parse(initial?.textContent || '[]'); return Array.isArray(parsed) ? parsed.filter(b => b && allowed.includes(b.type)).map(b => ({type:b.type,data:b.data && typeof b.data === 'object' ? b.data : {}})) : []; }
        catch { return []; }
    })();
    const defaults = {
        heading:()=>({text:'عنوان جديد',level:2}), paragraph:()=>({text:''}),
        list:()=>({items:['عنصر جديد'],ordered:false}), steps:()=>({items:[{title:'الخطوة الأولى',text:''}]}),
        callout:()=>({tone:'info',title:'معلومة مهمة',text:''}), image:()=>({src:'',alt:'',caption:''}),
        table:()=>({headers:['العمود الأول','العمود الثاني'],rows:[['','']]}), code:()=>({language:'text',code:''}),
        mermaid:()=>({source:'graph TD\n  A[البداية] --> B[الخطوة التالية]'}), link:()=>({label:'افتح الرابط',url:'https://'}), divider:()=>({})
    };
    const field = (label, key, value, options = {}) => {
        const wrap = document.createElement('label'); wrap.className = `block-field${options.full ? ' full' : ''}`;
        const title = document.createElement('span'); title.textContent = label; wrap.append(title);
        let control;
        if (options.options) {
            control = document.createElement('select');
            for (const [val,text] of options.options) { const o=document.createElement('option'); o.value=val; o.textContent=text; control.append(o); }
            control.value = esc(value ?? options.options[0][0]);
        } else if (options.multiline) {
            control=document.createElement('textarea'); control.value=esc(value); control.rows=options.rows || 3;
            if(options.mono) control.classList.add('mono-area'); if(options.tall) control.classList.add('tall');
            if(options.placeholder) control.placeholder=options.placeholder;
        } else {
            control=document.createElement('input'); control.type=options.number?'number':'text'; control.value=esc(value);
            if(options.number){control.min='1';control.max='6';control.step='1';}
            if(options.list)control.setAttribute('list',options.list);
            if(options.ltr){control.dir='ltr';control.style.textAlign='left';control.style.unicodeBidi='plaintext';}
            if(options.placeholder)control.placeholder=options.placeholder;
        }
        control.dataset.key=key; wrap.append(control);
        if(options.hint){const hint=document.createElement('small');hint.className='field-hint';hint.textContent=options.hint;wrap.append(hint);}
        return wrap;
    };
    const valueOf = (data,key,fallback='') => data[key] ?? fallback;
    function controlsFor(type,data){
        switch(type){
            case 'heading': return [field('نص العنوان','text',valueOf(data,'text'),{full:true}),field('مستوى العنوان','level',valueOf(data,'level',2),{options:[['2','عنوان رئيسي'],['3','عنوان فرعي'],['4','عنوان صغير']]})];
            case 'paragraph': return [field('نص الفقرة','text',valueOf(data,'text'),{full:true,multiline:true,tall:true})];
            case 'list': return [field('عناصر القائمة — كل عنصر في سطر','items',lines(data.items),{full:true,multiline:true,rows:4,hint:'يُحفظ كل سطر كعنصر مستقل.'}),field('نوع القائمة','ordered',data.ordered?'ordered':'unordered',{options:[['unordered','نقاط'],['ordered','مرقمة']]})];
            case 'steps': return [field('الخطوات — العنوان | الشرح في كل سطر','items',Array.isArray(data.items)?data.items.map(x=>`${x.title||''} | ${x.text||''}`).join('\n'):'',{full:true,multiline:true,rows:4,hint:'مثال: افتح الإعدادات | من القائمة الجانبية اختر الإعدادات.'})];
            case 'callout': return [field('نوع التنبيه','tone',valueOf(data,'tone','info'),{options:[['info','معلومة'],['tip','نصيحة'],['warning','تحذير'],['example','مثال']]}),field('العنوان','title',valueOf(data,'title','')),field('النص','text',valueOf(data,'text',''),{full:true,multiline:true})];
            case 'image': return [field('رابط الصورة','src',valueOf(data,'src'),{full:true,ltr:true,list:'cms-media-assets',placeholder:'Statics/img/BulkAll.png'}),field('النص البديل','alt',valueOf(data,'alt',''),{full:true}),field('التعليق','caption',valueOf(data,'caption',''),{full:true})];
            case 'table': return [field('عناوين الأعمدة — كل عنوان في سطر','headers',lines(data.headers),{full:true,multiline:true,rows:2}),field('صفوف البيانات — خلايا مفصولة بعلامة تبويب','rows',Array.isArray(data.rows)?data.rows.map(row=>Array.isArray(row)?row.join('\t'):'').join('\n'):'',{full:true,multiline:true,rows:4,hint:'افصل بين الخلايا بزر Tab.'})];
            case 'code': return [field('لغة البرمجة','language',valueOf(data,'language','text'),{ltr:true}),field('الكود','code',valueOf(data,'code'),{full:true,multiline:true,rows:6,mono:true,tall:true})];
            case 'mermaid': return [field('تعريف المخطط','source',valueOf(data,'source'),{full:true,multiline:true,rows:6,mono:true,hint:'اكتب صيغة Mermaid؛ سيحوّلها الموقع عند العرض.'})];
            case 'link': return [field('نص الرابط','label',valueOf(data,'label'),{full:true}),field('العنوان URL','url',valueOf(data,'url'),{full:true,ltr:true,placeholder:'https://example.com'})];
            default: return [];
        }
    }
    function readCard(card){
        const type=card.dataset.type; const data={};
        card.querySelectorAll('[data-key]').forEach(el=>{data[el.dataset.key]=el.value;});
        const layoutWidth = data.layout_width;
        const layoutAlign = data.layout_align;
        delete data.layout_width; delete data.layout_align;
        data.layout={width:allowedWidths.includes(layoutWidth)?layoutWidth:'full',align:allowedAlignments.includes(layoutAlign)?layoutAlign:'start'};
        if(type==='heading')data.level=Number(data.level)||2;
        if(type==='list'){data.items=esc(data.items).split(/\r?\n/).map(x=>x.trim()).filter(Boolean);data.ordered=data.ordered==='ordered';}
        if(type==='steps')data.items=esc(data.items).split(/\r?\n/).map(line=>{const i=line.indexOf('|');return {title:(i<0?line:line.slice(0,i)).trim(),text:(i<0?'':line.slice(i+1)).trim()};}).filter(x=>x.title||x.text);
        if(type==='table'){data.headers=esc(data.headers).split(/\r?\n/).map(x=>x.trim()).filter(Boolean);data.rows=esc(data.rows).split(/\r?\n/).filter(Boolean).map(line=>line.split('\t'));}
        return {type,data};
    }
    function textPreview(text,tag='p') {const el=document.createElement(tag);el.textContent=text;return el;}
    function paintPreview(){
        preview.replaceChildren();
        const valid=blocks.map((b,i)=>{const card=stack.children[i];return card?readCard(card):b;});
        if(!valid.length){const span=document.createElement('span');span.className='preview-placeholder';span.textContent='ستظهر هنا لمحة عن ترتيب المحتوى.';preview.append(span);return;}
        valid.forEach(({type,data},index)=>{
            const layout=data.layout&&typeof data.layout==='object'?data.layout:{};
            const width=allowedWidths.includes(layout.width)?layout.width:'full';
            const align=allowedAlignments.includes(layout.align)?layout.align:'start';
            const card=document.createElement('article');card.className=`canvas-block canvas-width-${width} canvas-align-${align}`;
            const order=document.createElement('span');order.className='canvas-order';order.textContent=String(index+1).padStart(2,'0');card.append(order);
            let content;
            if(type==='heading')content=textPreview(data.text||'عنوان جديد',Number(data.level)>2?'h4':'h3');
            else if(type==='paragraph')content=textPreview(data.text||'نص الفقرة');
            else if(type==='list'){content=document.createElement(data.ordered?'ol':'ul');(data.items||[]).slice(0,4).forEach(item=>content.append(textPreview(item,'li')));}
            else if(type==='steps')content=textPreview(`${(data.items||[]).length} خطوات إرشادية`);
            else if(type==='callout'){content=textPreview(data.title||data.text||'تنبيه');content.className='preview-chip';}
            else if(type==='image')content=textPreview(data.caption||data.alt||'صورة توضيحية');
            else if(type==='table'){content=document.createElement('table');content.className='preview-table';(data.rows||[]).slice(0,2).forEach(row=>{const tr=document.createElement('tr');row.forEach(cell=>tr.append(textPreview(cell,'td')));content.append(tr);});}
            else if(type==='code'||type==='mermaid')content=textPreview(type==='code'?'كتلة كود':'مخطط توضيحي');
            else if(type==='link'){content=textPreview(data.label||'رابط','span');content.className='preview-link-chip';}
            else if(type==='divider'){content=document.createElement('div');content.className='preview-rule';}
            if(content)card.append(content);
            preview.append(card);
        });
    }
    function updateCount(){count.textContent=`${blocks.length} ${blocks.length===1?'كتلة':'كتل'}`;workspace.classList.toggle('has-blocks',blocks.length>0);}
    function sync(){
        const result=Array.from(stack.children).map(readCard);hidden.value=JSON.stringify(result);blocks.splice(0,blocks.length,...result);updateCount();paintPreview();
    }
    function createCard(block,index){
        const type=block.type; const card=document.createElement('article');card.className='block-card';card.dataset.type=type;
        const top=document.createElement('header');top.className='block-top';
        const grip=document.createElement('span');grip.className='drag-grip';grip.textContent='⠿';grip.setAttribute('aria-hidden','true');grip.draggable=mode.value==='builder';top.append(grip);
        const label=document.createElement('span');label.className='block-kind';const icon=document.createElement('i');icon.textContent=marks[type];const name=document.createElement('span');name.textContent=names[type];label.append(icon,name);
        const position=document.createElement('span');position.className='block-position';position.textContent=`${String(index+1).padStart(2,'0')}`;position.dataset.position='';top.append(label,position);
        const addControl=(glyph,aria,action,extra='')=>{const btn=document.createElement('button');btn.type='button';btn.className=`block-control ${extra}`;btn.textContent=glyph;btn.setAttribute('aria-label',aria);btn.dataset.action=action;top.append(btn);};
        addControl('↑','نقل الكتلة إلى الأعلى','up');addControl('↓','نقل الكتلة إلى الأسفل','down');addControl('⧉','تكرار الكتلة','duplicate');addControl('×','حذف الكتلة','remove','remove');
        const data=block.data||{};const layout=data.layout&&typeof data.layout==='object'?data.layout:{};
        const fields=document.createElement('div');fields.className='block-fields';for(const item of controlsFor(type,data))fields.append(item);
        const layoutFields=document.createElement('div');layoutFields.className='block-layout-fields';
        layoutFields.append(field('عرض الكتلة','layout_width',allowedWidths.includes(layout.width)?layout.width:'full',{options:[['full','كامل'],['wide','واسع · ⅔'],['half','نصف'],['third','ثلث']]}));
        layoutFields.append(field('المحاذاة الأفقية','layout_align',allowedAlignments.includes(layout.align)?layout.align:'start',{options:[['start','البداية'],['center','الوسط'],['end','النهاية']]}));
        fields.append(layoutFields);
        card.append(top,fields);return card;
    }
    function redraw(){
        stack.replaceChildren();blocks.forEach((block,index)=>stack.append(createCard(block,index)));
        Array.from(stack.querySelectorAll('.block-card')).forEach((card,index)=>{card.querySelector('[data-action="up"]').disabled=index===0;card.querySelector('[data-action="down"]').disabled=index===blocks.length-1;card.draggable=false;const grip=card.querySelector('.drag-grip');if(grip)grip.draggable=mode.value==='builder';});
        updateCount();paintPreview();
    }
    function markDirty(){status.classList.add('is-dirty');statusLabel.textContent='توجد تغييرات غير محفوظة';}
    form.querySelectorAll('[data-add]').forEach(button=>button.addEventListener('click',()=>{
        const type=button.dataset.add;if(!defaults[type])return;blocks.push({type,data:defaults[type]()});redraw();markDirty();
        const last=stack.lastElementChild;last?.classList.add('is-selected');last?.scrollIntoView({block:'nearest',behavior:'smooth'});last?.querySelector('input,textarea,select')?.focus({preventScroll:true});
    }));
    stack.addEventListener('click',event=>{
        const btn=event.target.closest('[data-action]');if(!btn)return;const card=btn.closest('.block-card');const index=Array.from(stack.children).indexOf(card);if(index<0)return;
        let movedTo=null;let preferredMove=null;
        if(btn.dataset.action==='remove')blocks.splice(index,1);
        if(btn.dataset.action==='duplicate')blocks.splice(index+1,0,JSON.parse(JSON.stringify(readCard(card))));
        if(btn.dataset.action==='up'&&index>0){[blocks[index-1],blocks[index]]=[blocks[index],blocks[index-1]];movedTo=index-1;preferredMove='up';}
        if(btn.dataset.action==='down'&&index<blocks.length-1){[blocks[index+1],blocks[index]]=[blocks[index],blocks[index+1]];movedTo=index+1;preferredMove='down';}
        redraw();markDirty();
        if(movedTo!==null){const movedCard=stack.children[movedTo];const preferred=movedCard?.querySelector(`[data-action="${preferredMove}"]`);const fallbackMove=preferredMove==='up'?'down':'up';const fallback=movedCard?.querySelector(`[data-action="${fallbackMove}"]`);(preferred&&!preferred.disabled?preferred:fallback&&!fallback.disabled?fallback:null)?.focus();}
    });
    let dragSource=null;
    stack.addEventListener('dragstart',event=>{
        const grip=event.target.closest?.('.drag-grip');const card=grip?.closest('.block-card');
        if(mode.value!=='builder'||!grip||!card){event.preventDefault();return;}
        dragSource=card;card.classList.add('is-dragging');
        if(event.dataTransfer){event.dataTransfer.effectAllowed='move';event.dataTransfer.setData('text/plain',String(Array.from(stack.children).indexOf(card)));}
    });
    stack.addEventListener('dragover',event=>{
        const target=event.target.closest('.block-card');
        if(mode.value!=='builder'||!dragSource||!target||target===dragSource)return;
        event.preventDefault();stack.querySelectorAll('.drag-over').forEach(item=>item.classList.remove('drag-over'));target.classList.add('drag-over');
        if(event.dataTransfer)event.dataTransfer.dropEffect='move';
    });
    stack.addEventListener('drop',event=>{
        const target=event.target.closest('.block-card');
        if(mode.value!=='builder'||!dragSource||!target||target===dragSource)return;
        event.preventDefault();
        const cards=Array.from(stack.children);const from=cards.indexOf(dragSource);const targetIndex=cards.indexOf(target);
        if(from<0||targetIndex<0)return;
        const after=event.clientY>target.getBoundingClientRect().top+target.getBoundingClientRect().height/2;
        const current=cards.map(readCard);const [moved]=current.splice(from,1);let insertAt=targetIndex+(after?1:0);if(from<insertAt)insertAt--;current.splice(Math.max(0,insertAt),0,moved);
        blocks.splice(0,blocks.length,...current);dragSource=null;redraw();markDirty();
    });
    stack.addEventListener('dragend',()=>{dragSource=null;stack.querySelectorAll('.is-dragging,.drag-over').forEach(item=>item.classList.remove('is-dragging','drag-over'));});
    stack.addEventListener('input',()=>{sync();markDirty();});stack.addEventListener('change',()=>{sync();markDirty();});
    form.querySelectorAll('input:not([type=hidden]),select').forEach(el=>el.addEventListener('input',markDirty));
    const legacyNote=document.createElement('p');legacyNote.className='mode-note';legacyNote.textContent='هذا القسم يستخدم قالب الصفحة الحالي. اختر المحرر المرئي لتعديل كتل المحتوى.';legacyNote.hidden=true;composer.insertBefore(legacyNote,composer.querySelector('.composer-toolbar'));
    function updateMode(){const visual=mode.value==='builder';composer.classList.toggle('mode-disabled',!visual);composer.setAttribute('aria-disabled',String(!visual));legacyNote.hidden=visual;document.querySelector('[data-source-panel="legacy"]')?.toggleAttribute('hidden',visual);document.querySelector('[data-source-panel="builder"]')?.toggleAttribute('hidden',!visual);composer.querySelectorAll('[data-add],.block-control,.block-fields input,.block-fields textarea,.block-fields select').forEach(control=>{control.disabled=!visual;});stack.querySelectorAll('.drag-grip').forEach(grip=>{grip.draggable=visual;});}
    mode.addEventListener('change',()=>{updateMode();markDirty();});
    document.querySelector('#delete-section-form')?.addEventListener('submit',event=>{if(!window.confirm('سيُحذف هذا القسم ومحتواه نهائياً. هل تريد المتابعة؟'))event.preventDefault();});
    form.addEventListener('submit',()=>{sync();statusLabel.textContent='جارٍ إرسال التغييرات…';});
    redraw();updateMode();status.classList.remove('is-dirty');
})();
