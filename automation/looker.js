// Executed by the pinned Playwright MCP browser_run_code_unsafe tool.
// UI events only: no application internals, hidden APIs, or direct style mutations.
async function lookerAction(page, args) {
  const url = page.url();
  if (!/^https:\/\/(lookerstudio|datastudio)\.google\.com\//.test(url) ||
      !url.split('?')[0].includes('/reporting/' + args.report_id + '/'))
    throw Error('WRONG_REPORT: open the authorized report before calling this tool.');
  await page.bringToFront();
  const canvas = page.locator('.ng2-canvas-container');
  const panel = page.locator('article.property-panel');
  const colorKeys = {background:'background', title:'chartTitleColor', text:'fontColor',
    border:'borderColor', legend:'legendColor', plot_background:'chartbg',
    table_header:'headerColor', table_header_text:'headerFontColor',
    table_even:'oddRowColor', table_odd:'evenRowColor', axis:'axisLineColor',
    x_labels:'hAxisLabelsColor', y_labels:'leftYAxisLabelsColor', grid:'leftVGridLineColor'};
  const icons = {table:'table_chart', scorecard:'scorecard', bar:'bar_chart',
    pie:'pie_chart', time_series:'line_chart', pivot:'pivot_table'};
  const pauseUntil = async (fn, value) => page.waitForFunction(fn, value,
    {polling:100, timeout:8000});
  const click = async loc => {
    if (await loc.count() !== 1) throw Error('AMBIGUOUS_CONTROL: expected one UI control.');
    await loc.evaluate(e => {
      if (e.disabled || e.getAttribute('aria-disabled') === 'true') throw Error('DISABLED_CONTROL');
      e.click();
    });
  };
  const inventory = async () => canvas.evaluate(e => ({
    page_id:location.pathname.match(/\/page\/([^/]+)/)?.[1]||null,
    canvas:{width:e.offsetWidth, height:e.offsetHeight, scale:e.getBoundingClientRect().width/e.offsetWidth},
    components:Array.from(e.querySelectorAll(':scope > .lego-component-repeat')).map(w => {
      const c=w.querySelector('.lego-component');
      return {id:Array.from(c?.classList||[]).find(x=>/^cd-[\w-]+$/.test(x)),
        type:Array.from(c?.classList||[]).filter(x=>!['lego-component','selected'].includes(x)&&!x.startsWith('cd-')).join(' '),
        title:w.querySelector('.chart-title')?.textContent?.trim()||'', selected:c?.classList.contains('selected'),
        x:parseFloat(w.style.left),y:parseFloat(w.style.top),width:parseFloat(w.style.width),height:parseFloat(w.style.height)};
    })
  }));
  const get = async id => {
    const item=(await inventory()).components.find(x=>x.id===id);
    if (!item) throw Error('COMPONENT_NOT_FOUND: refresh looker_inventory.');
    return item;
  };
  if (args.action === 'inventory') return await inventory();
  if (!url.split('?')[0].endsWith('/edit')) throw Error('NOT_EDIT_MODE: enter Edit first.');
  if (await canvas.count() !== 1) throw Error('UNSUPPORTED_LAYOUT: expected one freeform canvas.');
  if(await page.getByRole('dialog').count()) throw Error('OPEN_DIALOG: finish the dialog before editing.');
  const dismiss = async host => {
    if(!await host.count()) return;
    await host.evaluate(e=>{
      const pane=e.closest('.cdk-overlay-pane');
      const backdrop=pane?.parentElement?.querySelector('.cdk-overlay-backdrop');
      if(!backdrop) throw Error('PICKER_CLOSE_UNAVAILABLE');
      backdrop.click();
    });
    await host.waitFor({state:'hidden',timeout:8000});
  };
  // A failed field search can leave its picker open. Dismiss only these pickers,
  // never an edit/confirmation dialog, before selecting a different component.
  for(let i=0;i<3;i++) {
    const pickers=page.locator('ng2-selector-dialog, datasource-selector-dialog');
    const count=await pickers.count();
    if(!count) break;
    if(await page.getByRole('dialog').count()) throw Error('OPEN_DIALOG: finish the dialog before editing.');
    await dismiss(pickers.last());
  }
  if(await page.locator('.cdk-overlay-pane input[type=search]').count()) throw Error('OPEN_PICKER: close the field picker before retrying.');
  const component = id => canvas.locator('.lego-component.' + id);
  const select = async id => {
    await get(id);
    await component(id).evaluate(e => {
      const r=e.getBoundingClientRect(), o={bubbles:true,cancelable:true,view:window,button:0,clientX:r.x+10,clientY:r.y+10};
      e.dispatchEvent(new MouseEvent('mousedown',{...o,buttons:1}));
      e.dispatchEvent(new MouseEvent('mouseup',{...o,buttons:0}));
      e.dispatchEvent(new MouseEvent('click',o));
    });
    await pauseUntil(id=>document.querySelector('.lego-component.'+id)?.classList.contains('selected'),id);
    const selected=(await inventory()).components.filter(c=>c.selected);
    if (selected.length!==1 || selected[0].id!==id) throw Error('SELECTION_MISMATCH');
  };
  const tab = async style => click(panel.getByRole('tab',{name:style?/^(Estilo|Style)$/:/^(Configuración|Setup)$/}));
  const cell = key => panel.locator('[data-webdriver-cell-key="'+key+'"]');
  const fieldKeys = {metric:'metrics',dimension:'actionConceptList',pivot_row:'pivotTableRowDimensions',pivot_column:'pivotTableColDimensions'};
  const sourceName = async () => (await cell('datasource').locator('.datasource-name-label').innerText()).trim();
  const chartIssues = async id => component(id).evaluate(e=>{
    const text=e.innerText;
    return ['Sin acceso al conjunto de datos','No data set access','No access to data set',
      'Error de configuración','Configuration error','Invalid field','Campo no válido',
      'No hay datos','No data'].filter(message=>text.toLowerCase().includes(message.toLowerCase()));
  });
  const inspect = async id => {
    await select(id); await tab(false);
    return {...await get(id),source:await sourceName(),issues:await chartIssues(id),fields:await panel.locator('[data-webdriver-cell-key]').evaluateAll(es=>
      es.filter(e=>e.innerText.trim()).map(e=>({key:e.getAttribute('data-webdriver-cell-key'),text:e.innerText.trim()})))};
  };
  if (args.action === 'inspect') return await inspect(args.component_id);
  if (args.action === 'create') {
    const before=await inventory();
    if (!icons[args.type]) throw Error('UNSUPPORTED_CHART_TYPE');
    if (args.x+args.width>before.canvas.width || args.y+args.height>before.canvas.height)
      throw Error('OUTSIDE_CANVAS: requested rectangle exceeds the page.');
    await click(page.getByRole('button',{name:/^(Insertar|Insert)$/}));
    await click(page.getByRole('menuitem').filter({has:page.locator('mat-icon[data-mat-icon-name="'+icons[args.type]+'"]')}));
    await canvas.evaluate((e,a)=>{
      const b=e.getBoundingClientRect(),sx=b.width/e.offsetWidth,sy=b.height/e.offsetHeight;
      const x=b.x+a.x*sx,y=b.y+a.y*sy,ex=x+a.width*sx,ey=y+a.height*sy;
      const o={bubbles:true,cancelable:true,view:window,button:0};
      e.dispatchEvent(new MouseEvent('mousemove',{...o,clientX:x,clientY:y,buttons:0}));
      e.dispatchEvent(new MouseEvent('mousedown',{...o,clientX:x,clientY:y,buttons:1}));
      document.dispatchEvent(new MouseEvent('mousemove',{...o,clientX:ex,clientY:ey,buttons:1}));
      document.dispatchEvent(new MouseEvent('mouseup',{...o,clientX:ex,clientY:ey,buttons:0}));
    },args);
    await pauseUntil(n=>document.querySelectorAll('.ng2-canvas-container > .lego-component-repeat').length>n,before.components.length);
    const created=(await inventory()).components.filter(c=>!before.components.some(b=>b.id===c.id));
    if (created.length!==1) throw Error('CREATION_UNCERTAIN: inspect inventory; do not retry blindly.');
    let c=created[0];
    if(!['x','y','width','height'].every(k=>Math.abs(c[k]-args[k])<=2)) {
      try {
        const adjusted=await lookerAction(page,{...args,action:'layout',component_id:c.id});
        c=adjusted.after;
      } catch(error) {
        return {component:await get(c.id),geometry_verified:false,fields_configured:false,
          error:'CREATED_BUT_LAYOUT_UNVERIFIED: '+error.message, next:'Inspect this component; do not create it again.'};
      }
    }
    const geometryMatches=['x','y','width','height'].every(k=>Math.abs(c[k]-args[k])<=2);
    return {component:c,geometry_verified:geometryMatches,fields_configured:false,
      next:'Use looker_set_field and looker_set_title. Creation uses the current default data source.'};
  }
  await select(args.component_id);
  if (args.action === 'sources' || args.action === 'set_source') {
    await tab(false);
    const before=await sourceName();
    if(args.action==='set_source'&&before===args.source)
      return {component_id:args.component_id,source:before,source_verified:true,unchanged:true,issues:await chartIssues(args.component_id),data_verified:false};
    await click(cell('datasource').locator('.right-side'));
    const picker=page.locator('datasource-selector-dialog');
    await picker.locator('.datasource-option').first().waitFor({state:'visible',timeout:8000});
    try {
      if(args.action==='sources') {
        return {component_id:args.component_id,current:before,sources:await picker.evaluate(root=>{
          let scope='unknown';const rows=[];
          for(const e of root.querySelectorAll('.header-label,.datasource-option')) {
            if(e.classList.contains('header-label')) {
              scope=/^(Fuentes de datos añadidas|Added data sources)$/i.test(e.textContent.trim())?'added':
                /^(Fuentes de datos disponibles|Available data sources)$/i.test(e.textContent.trim())?'available':'unknown';
            } else rows.push({name:e.querySelector('.right-side')?.textContent.trim(),scope,
              connector:e.querySelector('mat-icon[data-mat-icon-name]')?.getAttribute('data-mat-icon-name')});
          }
          return rows;
        }),access_verified:false};
      }
      await picker.evaluate((root,name)=>{
        const rows=Array.from(root.querySelectorAll('.datasource-option .right-side')).filter(e=>e.textContent.trim()===name);
        if(rows.length!==1) throw Error(rows.length?'AMBIGUOUS_SOURCE: use an unambiguous source name.':'SOURCE_NOT_FOUND: call looker_sources first.');
        rows[0].click();
      },args.source);
      await pauseUntil(name=>document.querySelector('article.property-panel [data-webdriver-cell-key=datasource] .datasource-name-label')?.textContent.trim()===name,args.source);
      return {component_id:args.component_id,before,source:await sourceName(),source_verified:true,
        data_verified:false,issues:await chartIssues(args.component_id),
        next:'Inspect available fields and remap chart fields. A selected source does not prove access or valid data.'};
    } finally { await dismiss(picker); }
  }
  if(args.action==='fields') {
    await tab(false);
    const current=await get(args.component_id);
    const slot=args.slot||'metric',key=slot==='metric'&&current.type.includes('simple-piechart')?'pieMetric':fieldKeys[slot];
    const chip=cell(key).locator('.right-half').first();
    if(!await chip.count()) throw Error('FIELD_SLOT_NOT_FOUND: choose a slot shown by looker_inspect.');
    const source=await sourceName();
    await click(chip);
    const picker=page.locator('ng2-selector-dialog');
    const query=args.query||'',limit=args.limit||40;
    try {
      await picker.locator('input[type=search]').fill(query);
      // The UI debounces search; allow its input handler to publish the filtered list.
      await page.waitForTimeout(400);
      await pauseUntil(q=>{
        const root=document.querySelector('ng2-selector-dialog');
        const names=Array.from(root?.querySelectorAll('.display-name')||[]);
        return root?.querySelector('.no-options-text')||names.length>0&&names.every(e=>e.textContent.toLowerCase().includes(q.toLowerCase()));
      },query);
      if(await picker.locator('.no-options-text').isVisible())
        return {source,slot,query,fields:[],has_more:false,next:'No matching fields. Check the source and try a broader query; do not invent a field.'};
      const viewport=picker.locator('.cdk-virtual-scroll-viewport');
      const fields=new Map();let hasMore=true;
      for(let pass=0;pass<12;pass++) {
        const rows=await picker.locator('.common-chip').evaluateAll(es=>es.map(e=>{
          let row=e.closest('.chip');while(row&&!row.classList.contains('group-label')) row=row.previousElementSibling;
          return {name:e.querySelector('.display-name')?.textContent.trim(),group:row?.textContent.trim()||'',
            type:e.querySelector('mat-icon[data-mat-icon-name]')?.getAttribute('data-mat-icon-name')||'unknown'};
        }));
        for(const row of rows) if(row.name) {
          const existing=fields.get(row.name);
          if(!existing||/^(Grupo predeterminado|Default group)$/.test(row.group)) fields.set(row.name,row);
        }
        const state=await viewport.evaluate(e=>({top:e.scrollTop,max:e.scrollHeight-e.clientHeight,height:e.clientHeight}));
        hasMore=state.top<state.max-1;
        if(fields.size>=limit||!hasMore) break;
        await viewport.evaluate((e,step)=>{e.scrollTop+=step;},Math.max(28,state.height-56));
        await page.waitForTimeout(80);
      }
      return {source,slot,query,fields:Array.from(fields.values()).slice(0,limit),has_more:hasMore||fields.size>limit,
        next:hasMore?'Narrow query to discover additional fields.':'Field names and types are UI metadata; validate grain and aggregation separately.'};
    } finally { await dismiss(picker); }
  }
  if(args.action==='inspect_style'||args.action==='set_color') {
    await tab(true);
    const readColors=async()=>panel.evaluate((root,keys)=>{
      const colors={};
      for(const [property,key] of Object.entries(keys)) {
        const swatch=root.querySelector('[data-webdriver-cell-key="'+key+'"] .color-preview-cell');
        if(swatch) colors[property]=getComputedStyle(swatch).backgroundColor;
      }
      const series=Array.from(root.querySelectorAll('[data-webdriver-cell-key=multiColor] .swatch')).map((e,index)=>({index,
        color:getComputedStyle(e).backgroundColor,enabled:getComputedStyle(e).cursor!=='no-drop'})).filter(s=>s.enabled);
      return {colors,series};
    },colorKeys);
    if(args.action==='inspect_style') return {component_id:args.component_id,...await readColors()};
    const property=args.property,index=args.series_index||0;
    const key=colorKeys[property];
    const preview=property==='series'?cell('multiColor').locator('.swatch').nth(index):cell(key).locator('.color-preview-cell');
    if(await preview.count()!==1) throw Error('UNSUPPORTED_COLOR: use looker_inspect_style to discover available properties.');
    if(property==='series'&&await preview.evaluate(e=>getComputedStyle(e).cursor==='no-drop')) throw Error('SERIES_DISABLED: configure a valid metric before coloring this series.');
    const before=await preview.evaluate(e=>getComputedStyle(e).backgroundColor);
    const rgb='rgb('+[1,3,5].map(i=>parseInt(args.color.slice(i,i+2),16)).join(', ')+')';
    if(before!==rgb) {
      await click(property==='series'?preview:cell(key).locator('color-picker-input button'));
      const palette=page.locator('color-dialog');
      await palette.waitFor({state:'visible',timeout:8000});
      const found=await palette.evaluate((root,color)=>{
        const match=Array.from(root.querySelectorAll('[role=button][aria-label]')).find(e=>e.getAttribute('aria-label').toLowerCase()===color.toLowerCase());
        if(match) match.click();return !!match;
      },args.color);
      if(!found) {
        await click(palette.locator('.add-custom-button'));
        const custom=page.locator('custom-color-picker');
        const hex=custom.locator('input[aria-label=Hex]');
        await hex.fill(args.color); await hex.press('Tab');
        await click(custom.getByRole('button',{name:/^(Hecho|Done)$/}));
      }
      await pauseUntil(({key,index,series,rgb})=>{
        const e=series?document.querySelectorAll('[data-webdriver-cell-key=multiColor] .swatch')[index]:document.querySelector('[data-webdriver-cell-key="'+key+'"] .color-preview-cell');
        return e&&getComputedStyle(e).backgroundColor===rgb;
      },{key,index,series:property==='series',rgb});
      await page.locator('custom-color-picker, color-dialog').waitFor({state:'hidden',timeout:8000});
    }
    return {component_id:args.component_id,property,series_index:property==='series'?index:undefined,before,
      color:args.color.toLowerCase(),configuration_verified:true};
  }
  if (args.action === 'layout') {
    const before=await get(args.component_id), bounds=(await inventory()).canvas;
    if (args.x+args.width>bounds.width||args.y+args.height>bounds.height) throw Error('OUTSIDE_CANVAS');
    // Shift+arrow is a one-canvas-pixel nudge; unmodified arrows snap to the grid.
    await component(args.component_id).evaluate((e,a)=>{
      const w=e.closest('.lego-component-repeat');
      for(const [axis,negative,positive,codes] of [['x','ArrowLeft','ArrowRight',[37,39]],['y','ArrowUp','ArrowDown',[38,40]]]) {
        const current=parseFloat(w.style[axis==='x'?'left':'top']);
        const delta=Math.round(a[axis]-current), key=delta<0?negative:positive, code=codes[delta<0?0:1];
        if(Math.abs(delta)>4000) throw Error('MOVE_TOO_LARGE');
        for(let i=0;i<Math.abs(delta);i++) for(const type of ['keydown','keyup'])
          e.dispatchEvent(new KeyboardEvent(type,{key,code:key,keyCode:code,which:code,shiftKey:true,bubbles:true,cancelable:true}));
      }
    },args);
    const moved=await get(args.component_id);
    if(Math.abs(moved.x-args.x)>1||Math.abs(moved.y-args.y)>1) throw Error('MOVE_UNVERIFIED: inspect before retrying.');
    if(Math.abs(moved.width-args.width)>1||Math.abs(moved.height-args.height)>1) {
      await canvas.locator('.selection-region resize-handler .bottom.right').evaluate((e,a)=>{
        const c=e.closest('.ng2-canvas-container'), b=c.getBoundingClientRect(),s=b.width/c.offsetWidth;
        const r=e.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2;
        const o={bubbles:true,cancelable:true,view:window,button:0};
        const ex=x+(a.width-a.currentWidth)*s,ey=y+(a.height-a.currentHeight)*s;
        e.dispatchEvent(new MouseEvent('mousedown',{...o,clientX:x,clientY:y,buttons:1}));
        document.dispatchEvent(new MouseEvent('mousemove',{...o,clientX:ex,clientY:ey,buttons:1}));
        document.dispatchEvent(new MouseEvent('mouseup',{...o,clientX:ex,clientY:ey,buttons:0}));
      },{...args,currentWidth:moved.width,currentHeight:moved.height});
    }
    const after=await get(args.component_id);
    if(!['x','y','width','height'].every(k=>Math.abs(after[k]-args[k])<=2)) throw Error('RESIZE_UNVERIFIED: inspect actual geometry.');
    return {before,after,geometry_verified:true};
  }
  if (args.action === 'set_field' || args.action === 'set_sort') {
    await tab(false);
    const current=await get(args.component_id);
    const sorting=args.action==='set_sort';
    if(sorting&&!['simple-table','simple-barchart','simple-piechart'].some(t=>current.type.includes(t)))
      throw Error('UNSUPPORTED_SORT: this operation currently supports tables, bars and pies.');
    const key=sorting?(current.type.includes('simple-table')?'sortConcept1':'sortConcept'):
      args.slot==='metric'&&current.type.includes('simple-piechart')?'pieMetric':fieldKeys[args.slot], index=args.index||0;
    const complete = async unchanged => {
      if(sorting) {
        const dirKey=current.type.includes('simple-table')?'sortDir1':'sortDir';
        const value=args.direction==='ascending'?'0':'1';
        const radio=cell(dirKey).locator('input[type=radio][value="'+value+'"]');
        if(!await radio.isChecked()) await click(radio);
        await pauseUntil(({key,value})=>document.querySelector('[data-webdriver-cell-key="'+key+'"] input[value="'+value+'"]')?.checked,{key:dirKey,value});
        return {component_id:args.component_id,field:args.field,direction:args.direction,configuration_verified:true};
      }
      return {component_id:args.component_id,slot:args.slot,index,field:args.field,verified:true,unchanged};
    };
    const chips=cell(key).locator('.right-half');
    if(await chips.count()<=index) throw Error('FIELD_SLOT_NOT_FOUND: this operation replaces an existing field; inspect chart slots.');
    if((await chips.nth(index).locator('.display-name').textContent()).trim()===args.field)
      return await complete(true);
    await click(chips.nth(index));
    const overlay=page.locator('.cdk-overlay-container');
    await overlay.locator('input[type=search]').fill(args.field);
    await pauseUntil(field=>Array.from(document.querySelectorAll('.cdk-overlay-container .display-name')).some(e=>e.textContent.trim()===field),args.field);
    await overlay.evaluate((root,field)=>{
      const matches=Array.from(root.querySelectorAll('.display-name')).filter(e=>e.textContent.trim()===field);
      const sourceMatches=matches.filter(e=>{
        let row=e.closest('.chip');
        while(row&&!row.classList.contains('group-label')) row=row.previousElementSibling;
        return row&&/^(Grupo predeterminado|Default group)$/.test(row.textContent.trim());
      });
      const candidates=sourceMatches.length?sourceMatches:matches;
      if(candidates.length!==1) throw Error('AMBIGUOUS_FIELD: exact name matches multiple source fields.');
      candidates[0].click();
    },args.field);
    await pauseUntil(({key,index,field})=>{
      const es=document.querySelectorAll('[data-webdriver-cell-key="'+key+'"] .right-half .display-name');
      return es[index]?.textContent.trim()===field;
    },{key,index,field:args.field});
    return await complete(false);
  }
  if (args.action === 'set_title') {
    await tab(true);
    const show=cell('chartTitleShowTitle').getByRole('switch');
    if(await show.getAttribute('aria-checked')!=='true') await click(show);
    const input=cell('chartTitleText').locator('input');
    await input.fill(args.title); await input.press('Tab');
    await pauseUntil(({id,title})=>document.querySelector('.lego-component.'+id)?.closest('.lego-component-repeat')?.querySelector('.chart-title')?.textContent.trim()===title,
      {id:args.component_id,title:args.title});
    return {...await get(args.component_id),title_verified:true};
  }
  throw Error('UNKNOWN_ACTION');
}
