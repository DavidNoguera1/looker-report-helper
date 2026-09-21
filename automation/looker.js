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
  // A failed field search can leave its picker open. Dismiss only these pickers,
  // never an edit/confirmation dialog, before selecting a different component.
  for(let i=0;i<3;i++) {
    const count=await page.locator('.cdk-overlay-pane input[type=search]').count();
    if(!count) break;
    if(await page.getByRole('dialog').count()) throw Error('OPEN_DIALOG: finish the dialog before editing.');
    await click(page.locator('.cdk-overlay-backdrop-showing').last());
    await pauseUntil(n=>document.querySelectorAll('.cdk-overlay-pane input[type=search]').length<n,count);
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
  const inspect = async id => {
    await select(id); await tab(false);
    return {...await get(id),fields:await panel.locator('[data-webdriver-cell-key]').evaluateAll(es=>
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
