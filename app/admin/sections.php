<?php
require __DIR__ . '/_bootstrap.php';
$user = admin_require_role('admin');
$pdo = codefy_db();
// This controller uses the same section registry and URL resolver as the public guide.
require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/content-blocks.php';

$coreSlugs = ['login','bulk-import','relationships','assignments','pricing','readiness','analysis-config'];
$accentOptions = ['primary','indigo','emerald','amber','violet','rose','cyan'];
$blockTypes = ['heading','paragraph','list','steps','callout','image','table','code','mermaid','link','divider'];
$scalarText = static function (array $source, string $key, string $default = ''): string {
    $value = $source[$key] ?? $default;
    if (!is_string($value)) throw new InvalidArgumentException('أحد الحقول النصية غير صالح.');
    return $value;
};

$requiredText = static function (array $source, string $key, int $max, bool $required = true): string {
    $raw = $source[$key] ?? '';
    if (!is_scalar($raw)) throw new InvalidArgumentException('أحد الحقول النصية غير صالح.');
    $value = trim((string)$raw);
    if (($required && $value === '') || strlen($value) > $max) {
        throw new InvalidArgumentException('يرجى مراجعة الحقول النصية المطلوبة وحدود طولها.');
    }
    return $value;
};
$validateBlocks = static function ($raw) use ($blockTypes, $requiredText): array {
    if (!is_string($raw) || strlen($raw) > 500000) throw new InvalidArgumentException('محتوى الصفحة أكبر من الحد المسموح.');
    $input = json_decode($raw, true, 32, JSON_THROW_ON_ERROR);
    if (!is_array($input) || count($input) > 100) throw new InvalidArgumentException('يجب أن يكون محتوى الصفحة قائمة تضم 100 كتلة أو أقل.');
    $blocks = [];
    foreach ($input as $block) {
        if (!is_array($block) || !in_array(($block['type'] ?? null), $blockTypes, true) || !is_array($block['data'] ?? null)) {
            throw new InvalidArgumentException('تحتوي الصفحة على كتلة غير صالحة.');
        }
        $type = $block['type'];
        $data = $block['data'];
        switch ($type) {
            case 'heading':
                $level = filter_var($data['level'] ?? 2, FILTER_VALIDATE_INT);
                if (!in_array($level, [2,3,4], true)) throw new InvalidArgumentException('مستوى العنوان غير صالح.');
                $safe = ['text'=>$requiredText($data,'text',500),'level'=>$level];
                break;
            case 'paragraph':
                $safe = ['text'=>$requiredText($data,'text',12000)];
                break;
            case 'list':
                $items = $data['items'] ?? [];
                if (!is_array($items) || count($items) > 80) throw new InvalidArgumentException('القائمة غير صالحة أو طويلة جداً.');
                foreach ($items as $item) if (!is_scalar($item)) throw new InvalidArgumentException('تحتوي القائمة على عنصر غير صالح.');
                $items = array_values(array_filter(array_map(static fn($v)=>trim((string)$v),$items),static fn($v)=>$v!==''));
                if (!$items || array_filter($items,static fn($v)=>strlen($v)>1500)) throw new InvalidArgumentException('أضف عناصر قصيرة وصحيحة للقائمة.');
                $safe = ['items'=>$items,'ordered'=>filter_var($data['ordered']??false,FILTER_VALIDATE_BOOLEAN)];
                break;
            case 'steps':
                $items = $data['items'] ?? [];
                if (!is_array($items) || !$items || count($items)>40) throw new InvalidArgumentException('أضف خطوة واحدة على الأقل وبحد أقصى 40 خطوة.');
                $safeItems=[];
                foreach($items as $item){
                    if(!is_array($item)) throw new InvalidArgumentException('تنسيق الخطوات غير صالح.');
                    $safeItems[]=['title'=>$requiredText($item,'title',240),'text'=>$requiredText($item,'text',2000,false)];
                }
                $safe=['items'=>$safeItems];
                break;
            case 'callout':
                $tone=$scalarText($data,'tone','info');
                if(!in_array($tone,['info','tip','warning','example'],true)) throw new InvalidArgumentException('نوع التنبيه غير صالح.');
                $safe=['tone'=>$tone,'title'=>$requiredText($data,'title',240,false),'text'=>$requiredText($data,'text',4000)];
                break;
            case 'image':
                $src=$requiredText($data,'src',2048);
                if(!codefy_content_url($src,true)) throw new InvalidArgumentException('رابط الصورة يجب أن يكون HTTPS أو من مجلد Statics/.');
                $safe=['src'=>$src,'alt'=>$requiredText($data,'alt',500,false),'caption'=>$requiredText($data,'caption',500,false)];
                break;
            case 'table':
                $headers=$data['headers']??[]; $rows=$data['rows']??[];
                if(!is_array($headers)||!$headers||count($headers)>12||!is_array($rows)||count($rows)>80) throw new InvalidArgumentException('بيانات الجدول غير صالحة.');
                foreach ($headers as $header) if (!is_scalar($header)) throw new InvalidArgumentException('عنوان عمود غير صالح.');
                $headers=array_values(array_map(static fn($v)=>trim((string)$v),$headers));
                if(array_filter($headers,static fn($v)=>$v===''||strlen($v)>240)) throw new InvalidArgumentException('كل عمود يحتاج عنواناً لا يتجاوز 240 بايت.');
                $safeRows=[];
                foreach($rows as $row){
                    if(!is_array($row)||count($row)!==count($headers)) throw new InvalidArgumentException('يجب أن يحتوي كل صف على خلية لكل عمود.');
                    foreach ($row as $cell) if (!is_scalar($cell)) throw new InvalidArgumentException('تحتوي خلية الجدول على قيمة غير صالحة.');
                    $cells=array_values(array_map(static fn($v)=>trim((string)$v),$row));
                    if(array_filter($cells,static fn($v)=>strlen($v)>1500)) throw new InvalidArgumentException('إحدى خلايا الجدول أطول من الحد المسموح.');
                    $safeRows[]=$cells;
                }
                $safe=['headers'=>$headers,'rows'=>$safeRows];
                break;
            case 'code':
                $language=trim($scalarText($data,'language','text'));
                if(!preg_match('/^[a-zA-Z0-9_+-]{1,32}$/',$language)) throw new InvalidArgumentException('اسم لغة الكود غير صالح.');
                $safe=['language'=>$language,'code'=>$requiredText($data,'code',20000)];
                break;
            case 'mermaid':
                $safe=['source'=>$requiredText($data,'source',20000)];
                break;
            case 'link':
                $url=$requiredText($data,'url',2048);
                if(!codefy_content_url($url)) throw new InvalidArgumentException('الرابط يجب أن يكون HTTPS أو مساراً داخلياً آمناً.');
                $safe=['url'=>$url,'label'=>$requiredText($data,'label',500)];
                break;
            case 'divider':
                $safe=[];
                break;
        }
        $layout=$data['layout']??[];
        if(!is_array($layout)) throw new InvalidArgumentException('إعدادات موضع الكتلة غير صالحة.');
        $width=$layout['width']??'full';
        $align=$layout['align']??'start';
        if(!in_array($width,['full','wide','half','third'],true)||!in_array($align,['start','center','end'],true)) {
            throw new InvalidArgumentException('اختر حجماً وموضعاً صالحين للكتلة.');
        }
        $safe['layout']=['width'=>$width,'align'=>$align];
        $blocks[]=['type'=>$type,'data'=>$safe];
    }
    return $blocks;
};

if ($_SERVER['REQUEST_METHOD']==='POST') {
    admin_require_csrf();
    try {
        $action=(string)($_POST['action']??'');
        if($action==='delete_section'){
            $slug=$scalarText($_POST,'original_slug');
            if(!preg_match('/^[a-z0-9]+(?:-[a-z0-9]+)*$/',$slug)||in_array($slug,$coreSlugs,true)) throw new InvalidArgumentException('لا يمكن حذف هذا القسم الأساسي.');
            $pdo->beginTransaction();
            $pdo->query('SELECT pg_advisory_xact_lock(840713249)');
            $delete=$pdo->prepare('DELETE FROM codefy_guide_sections WHERE slug=:slug');
            $delete->execute(['slug'=>$slug]);
            if($delete->rowCount()!==1) throw new InvalidArgumentException('القسم المطلوب غير موجود.');
            $pdo->exec('UPDATE codefy_guide_sections SET sort_order=sort_order+10000');
            $remaining=$pdo->query('SELECT slug FROM codefy_guide_sections ORDER BY sort_order,slug')->fetchAll(PDO::FETCH_COLUMN);
            $renumber=$pdo->prepare('UPDATE codefy_guide_sections SET sort_order=:order WHERE slug=:slug');
            foreach($remaining as $index=>$remainingSlug) $renumber->execute(['order'=>$index+1,'slug'=>$remainingSlug]);
            codefy_admin_audit($pdo,(int)$user['id'],'delete','guide_section',$slug);
            $pdo->commit();
            admin_flash('success','تم حذف القسم ومحتواه.');
            header('Location: sections.php'); exit;
        }
        if($action!=='save_section') throw new InvalidArgumentException('الإجراء المطلوب غير معروف.');
        $originalSlug=trim($scalarText($_POST,'original_slug'));
        $isEdit=$originalSlug!=='';
        if($isEdit&&!preg_match('/^[a-z0-9]+(?:-[a-z0-9]+)*$/',$originalSlug)) throw new InvalidArgumentException('معرّف القسم الحالي غير صالح.');
        $slug=strtolower(trim($scalarText($_POST,'slug')));
        if(!preg_match('/^[a-z0-9]+(?:-[a-z0-9]+)*$/',$slug)||strlen($slug)>80) throw new InvalidArgumentException('استخدم أحرفاً إنجليزية صغيرة وأرقاماً وواصلات فقط لمعرّف الرابط.');
        $reserved=['index','section','admin','includes','statics','api'];
        if(!$isEdit&&(in_array($slug,$reserved,true)||is_file(dirname(__DIR__).DIRECTORY_SEPARATOR.$slug.'.php'))) throw new InvalidArgumentException('معرّف الرابط محجوز في التطبيق.');
        if($isEdit&&in_array($originalSlug,$coreSlugs,true)&&$slug!==$originalSlug) throw new InvalidArgumentException('معرّف صفحة النظام الأساسية لا يمكن تغييره.');
        $title=$requiredText($_POST,'title',160);
        $subtitle=$requiredText($_POST,'subtitle',240,false);
        $icon=$requiredText($_POST,'icon',32);
        $accent=$scalarText($_POST,'accent','primary');
        $mode=$scalarText($_POST,'content_mode',$isEdit?'legacy':'builder');
        $published=isset($_POST['is_published'])&&$_POST['is_published']==='1';
        $order=filter_var($_POST['sort_order']??null,FILTER_VALIDATE_INT);
        if(!in_array($accent,$accentOptions,true)||!in_array($mode,['legacy','builder'],true)||$order===false) throw new InvalidArgumentException('راجع لون القسم وطريقة المحتوى وترتيبه.');
        if(!$isEdit&&$mode==='legacy') throw new InvalidArgumentException('الأقسام الجديدة تستخدم المحرر المرئي.');
        $blocks=$mode==='builder'?$validateBlocks($_POST['blocks_json']??'[]'):[];
        if($published&&$mode==='builder'&&!$blocks) throw new InvalidArgumentException('أضف كتلة واحدة على الأقل قبل نشر صفحة المحرر المرئي.');
        $existingSlugs=$pdo->query('SELECT slug FROM codefy_guide_sections ORDER BY sort_order,slug')->fetchAll(PDO::FETCH_COLUMN);
        if($isEdit&&!in_array($originalSlug,$existingSlugs,true)) throw new InvalidArgumentException('القسم المطلوب غير موجود.');
        if((!$isEdit||$slug!==$originalSlug)&&in_array($slug,$existingSlugs,true)) throw new InvalidArgumentException('معرّف الرابط مستخدم بالفعل.');
        $maxOrder=count($existingSlugs)+($isEdit?0:1);
        if($order<1||$order>$maxOrder||$maxOrder>1000) throw new InvalidArgumentException('ترتيب القسم خارج النطاق المتاح.');
        if($isEdit&&!$published){
            $publishedCount=$pdo->prepare('SELECT count(*) FROM codefy_guide_sections WHERE is_published AND slug<>:slug');
            $publishedCount->execute(['slug'=>$originalSlug]);
            if((int)$publishedCount->fetchColumn()===0) throw new InvalidArgumentException('يجب إبقاء قسم واحد على الأقل منشوراً.');
        }
        $ordered=$existingSlugs;
        if($isEdit) $ordered=array_values(array_filter($ordered,static fn($existing)=>$existing!==$originalSlug));
        array_splice($ordered,$order-1,0,[$slug]);

        $pdo->beginTransaction();
        $pdo->query('SELECT pg_advisory_xact_lock(840713249)');
        if($existingSlugs) $pdo->exec('UPDATE codefy_guide_sections SET sort_order=sort_order+10000');
        if($isEdit){
            $stmt=$pdo->prepare('UPDATE codefy_guide_sections SET slug=:slug,title=:title,subtitle=:subtitle,icon=:icon,accent=:accent,content_mode=:mode,is_published=CAST(:published AS boolean),sort_order=20000,updated_at=now(),updated_by=:admin_id WHERE slug=:original_slug');
            $stmt->execute(['slug'=>$slug,'title'=>$title,'subtitle'=>$subtitle,'icon'=>$icon,'accent'=>$accent,'mode'=>$mode,'published'=>$published?'true':'false','admin_id'=>$user['id'],'original_slug'=>$originalSlug]);
        }else{
            $stmt=$pdo->prepare('INSERT INTO codefy_guide_sections(slug,title,subtitle,icon,accent,content_mode,is_published,sort_order,updated_by) VALUES(:slug,:title,:subtitle,:icon,:accent,:mode,CAST(:published AS boolean),20000,:admin_id)');
            $stmt->execute(['slug'=>$slug,'title'=>$title,'subtitle'=>$subtitle,'icon'=>$icon,'accent'=>$accent,'mode'=>$mode,'published'=>$published?'true':'false','admin_id'=>$user['id']]);
        }
        $renumber=$pdo->prepare('UPDATE codefy_guide_sections SET sort_order=:order WHERE slug=:slug');
        foreach($ordered as $index=>$orderedSlug) $renumber->execute(['order'=>$index+1,'slug'=>$orderedSlug]);
        if($mode==='builder'){
            $pdo->prepare('DELETE FROM codefy_section_blocks WHERE section_slug=:slug')->execute(['slug'=>$slug]);
            $insert=$pdo->prepare('INSERT INTO codefy_section_blocks(section_slug,block_type,payload,sort_order) VALUES(:slug,:type,CAST(:payload AS jsonb),:order)');
            foreach($blocks as $index=>$block) $insert->execute(['slug'=>$slug,'type'=>$block['type'],'payload'=>json_encode($block['data'],JSON_UNESCAPED_UNICODE|JSON_THROW_ON_ERROR),'order'=>$index+1]);
        }
        codefy_admin_audit($pdo,(int)$user['id'],$isEdit?'update':'create','guide_section',$slug,['title'=>$title,'blocks_saved'=>$mode==='builder'?count($blocks):null,'blocks_preserved'=>$mode==='legacy','published'=>$published,'content_mode'=>$mode]);
        $pdo->commit();
        admin_flash('success',$isEdit?'تم حفظ القسم ومحتواه.':'تم إنشاء القسم ومحتواه.');
        header('Location: sections.php?edit='.rawurlencode($slug)); exit;
    }catch(Throwable $exception){
        if($pdo->inTransaction()) $pdo->rollBack();
        error_log('Codefy section manager failed: '.$exception->getMessage());
        admin_flash('error',$exception instanceof InvalidArgumentException?$exception->getMessage():'تعذر حفظ القسم. تحقق من قاعدة البيانات وحاول مرة أخرى.');
        $fallback=trim((string)($_POST['original_slug']??''));
        header('Location: sections.php'.($fallback!==''?'?edit='.rawurlencode($fallback):'')); exit;
    }
}

$sections=$pdo->query("SELECT s.slug,s.title,s.subtitle,s.icon,s.accent,s.content_mode,s.sort_order,s.is_published,(SELECT count(*) FROM codefy_section_blocks b WHERE b.section_slug=s.slug) AS block_count FROM codefy_guide_sections s ORDER BY s.sort_order,s.slug")->fetchAll();
foreach($sections as &$row) $row['public_url']='../'.codefy_section_url($row['slug']);
unset($row);
$sectionStats = ['published'=>0,'drafts'=>0,'blocks'=>0];
foreach ($sections as $section) {
    $sectionStats[!empty($section['is_published']) ? 'published' : 'drafts']++;
    $sectionStats['blocks'] += (int)($section['block_count'] ?? 0);
}
$editingSection=null; $blocks=[]; $isLegacyTemplate=false; $hasLegacyTemplate=false;
$editSlug=trim((string)($_GET['edit']??''));
if($editSlug!==''){
    $find=$pdo->prepare('SELECT slug,title,subtitle,icon,accent,content_mode,sort_order,is_published FROM codefy_guide_sections WHERE slug=:slug');
    $find->execute(['slug'=>$editSlug]); $editingSection=$find->fetch()?:null;
    if(!$editingSection){http_response_code(404);exit('القسم المطلوب غير موجود.');}
    $hasLegacyTemplate=is_file(dirname(__DIR__).DIRECTORY_SEPARATOR.$editingSection['slug'].'.php');
    $isLegacyTemplate=$editingSection['content_mode']==='legacy'&&$hasLegacyTemplate;
    $editingSection['public_url']=$hasLegacyTemplate?'../'.rawurlencode($editingSection['slug']).'.php':'../'.codefy_section_url($editingSection['slug']);
    $query=$pdo->prepare('SELECT block_type AS type,payload AS data FROM codefy_section_blocks WHERE section_slug=:slug ORDER BY sort_order,id');
    $query->execute(['slug'=>$editSlug]);
    foreach($query as $block){$data=$block['data'];if(is_string($data))$data=json_decode($data,true);$blocks[]=['type'=>$block['type'],'data'=>is_array($data)?$data:[]];}
}
$csrf=admin_csrf_token(); $flash=admin_take_flash();
$mediaAssets=[];
$mediaDir=dirname(__DIR__).DIRECTORY_SEPARATOR.'Statics'.DIRECTORY_SEPARATOR.'img';
foreach(glob($mediaDir.DIRECTORY_SEPARATOR.'*')?:[] as $mediaPath){
    if(is_file($mediaPath)&&preg_match('/\.(?:png|jpe?g|gif|webp|svg)$/i',$mediaPath)) $mediaAssets[]='Statics/img/'.basename($mediaPath);
}
sort($mediaAssets,SORT_NATURAL|SORT_FLAG_CASE);
require __DIR__.'/sections-view.php';
